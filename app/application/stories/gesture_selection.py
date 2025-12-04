from pydub import AudioSegment
import json
import os
import requests

CONCEPTNET_URL = "http://api.conceptnet.io/c/es/"

def load_gestures(folder):
    gestures = {}
    for file in os.listdir(folder):
        if file.endswith(".json"):
            with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
                gesture = json.load(f)
                gestures[gesture["gesture_id"]] = gesture
    return gestures

def add_segment_data(emotions_data, audio_dir):
    current_time = 0.0
    for idx, data in enumerate(emotions_data):
        audio_path = os.path.join(audio_dir, f"sentence_{idx}.wav")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file {audio_path} not found.")

        audio = AudioSegment.from_file(audio_path)
        duration = len(audio) / 1000.0

        data["segment"] = {
            "start": current_time,
            "end": current_time + duration,
            "duration": duration
        }

        current_time += duration

    return emotions_data

def query_conceptnet(word):
    url = f"{CONCEPTNET_URL}{word}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def select_contextual_gesture(sentence, contextual_gestures_library):
    words = sentence.split()
    for gesture_id, gesture in contextual_gestures_library.items():
        for keyword in gesture["keywords"]:
            if keyword in words:
                contextual_position = sentence.index(keyword)
                return gesture, contextual_position
    return None, None

def filtered_emotional_gestures(emotion, emotional_gestures_library):
    filtered_gestures = [gesture for gesture in emotional_gestures_library.values() if emotion in gesture["labels"]]
    return filtered_gestures

def select_gestures(gestures_path, audio_dir, emotions_data, min_silence_len=500, silence_thresh=-40):
    emotional_gestures_library = load_gestures(gestures_path + '/emotions')
    contextual_gestures_library = load_gestures(gestures_path + '/context')

    segments_data = add_segment_data(emotions_data, audio_dir)
    
    for data in segments_data:
        emotion = data["emotion"]
        contextual_gesture, contextual_position = select_contextual_gesture(data["sentence"], contextual_gestures_library)

        selected_gestures = []
        segments = []

        segment_complete = data["segment"]

        contextual_moment = 0
        contextual_duration = 0

        if contextual_gesture:
            segment_start = segment_complete["start"]
            segment_end = segment_complete["end"]
            segment_duration = segment_complete["duration"]

            contextual_duration = contextual_gesture["duration"]

            if contextual_duration > segment_duration:
                print(f"Contextual gesture '{contextual_gesture['gesture_id']}' exceeds segment. Compressing positions...")
                
                compression_factor = segment_duration / contextual_duration

                for position, position_data in contextual_gesture["frames"].items():
                    position_data["timestamp"] *= compression_factor

                contextual_gesture["duration"] = segment_duration
                contextual_moment = segment_start
            else:
                contextual_moment = segment_start + (contextual_position / len(data["sentence"])) * segment_complete["duration"]
                
                if contextual_moment + contextual_duration > segment_end:
                    contextual_moment = segment_end - contextual_duration

                segments.append({
                    "start": segment_start, 
                    "end": contextual_moment,       
                    "duration": contextual_moment - segment_start
                })
                segments.append({
                    "start": contextual_duration + contextual_moment, 
                    "end": segment_end,       
                    "duration": segment_end - (contextual_duration + contextual_moment)
                })
        else:
            segments.append(segment_complete)

        emotional_gestures = filtered_emotional_gestures(emotion, emotional_gestures_library)

        if contextual_gesture and not emotional_gestures or not segments:
            selected_gestures.append(contextual_gesture)
            data["gestures"] = selected_gestures
            continue

        if not contextual_gesture and not emotional_gestures:
            print(f"No gestures found for emotion: {emotion}, nor keywords")
            continue

        for idx, segment in enumerate(segments):
            total_duration = segment["duration"]
            start_segment = segment["start"]
            remaining_time = total_duration

            while remaining_time > 0:
                filtered_duration_gestures = [
                    gesture for gesture in emotional_gestures
                    if gesture["duration"] <= remaining_time
                ]

                if filtered_duration_gestures:
                    selected_gesture = max(filtered_duration_gestures, key=lambda g: g["duration"])
                    remaining_time -= selected_gesture["duration"]
                else:
                    original_gesture = max(emotional_gestures, key=lambda g: g["duration"])
                    positions = sorted(original_gesture["frames"].items(), key=lambda x: x[1]["timestamp"])
                    cut_positions = []
                    accumulated_duration = 0

                    for i in range(len(positions)):
                        name_position, position_data = positions[i]
                        timestamp = position_data["timestamp"]

                        if i + 1 < len(positions):
                            next_timestamp = positions[i + 1][1]["timestamp"]
                            position_duration = next_timestamp - timestamp
                        else:
                            position_duration = remaining_time - accumulated_duration

                        if accumulated_duration + position_duration > remaining_time:
                            position_duration = remaining_time - accumulated_duration

                        cut_positions.append((name_position, position_data))
                        accumulated_duration += position_duration

                        if accumulated_duration >= remaining_time:
                            break

                    selected_gesture = {
                        "gesture_id": f"{original_gesture['gesture_id']}_mod",
                        "labels": original_gesture["labels"],
                        "duration": accumulated_duration,
                        "frames": dict(cut_positions)
                    }

                    remaining_time -= accumulated_duration

                selected_gestures.append(selected_gesture)

            if idx == 0 and contextual_gesture:
                selected_gestures.append(contextual_gesture)

        data["gestures"] = selected_gestures

    return segments_data
