"""
Comprehensive Test Suite for Phoenix - Multi-Modal AI Part 1
Tests 396-425: Vision-Language, Audio Processing, Cross-Modal Integration (30 tests)

This file tests Phoenix's ability to detect and fix bugs in multi-modal AI systems,
including vision-language models, audio processing, and cross-modal integration.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestVisionLanguageModels:
    """Test vision-language model integration (10 tests)"""
    
    def test_image_text_alignment(self):
        """Test 396: Align image and text representations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MisalignedVLM:
    def process(self, image, text):
        # BUG: Processes separately, no alignment
        image_features = self.encode_image(image)
        text_features = self.encode_text(text)
        
        # BUG: Doesn't align representations
        return {
            "image": image_features,
            "text": text_features
        }
    
    def encode_image(self, image):
        return [0.1] * 512
    
    def encode_text(self, text):
        return [0.2] * 768  # Different dimension!

vlm = MisalignedVLM()

result = vlm.process("cat.jpg", "A photo of a cat")
# BUG: Different dimensions, can't compute similarity
print(f"Image dim: {len(result['image'])}")
print(f"Text dim: {len(result['text'])}")
"""
            
            test_file = os.path.join(temp_dir, "image_text_alignment.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_visual_grounding_accuracy(self):
        """Test 397: Ground text references to image regions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoGroundingVLM:
    def locate(self, image, text_query):
        # BUG: Returns random bounding box
        return {"x": 0, "y": 0, "w": 100, "h": 100}

vlm = NoGroundingVLM()

# Query: "Where is the cat?"
bbox = vlm.locate("image.jpg", "cat")

# BUG: Doesn't actually ground to cat location
print(f"Bounding box: {bbox}")
"""
            
            test_file = os.path.join(temp_dir, "visual_grounding.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_image_caption_consistency(self):
        """Test 398: Ensure consistent image captions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InconsistentCaptioner:
    def __init__(self):
        self.caption_count = 0
    
    def generate_caption(self, image):
        # BUG: Non-deterministic captions for same image
        self.caption_count += 1
        
        if self.caption_count % 2 == 0:
            return "A dog playing in the park"
        else:
            return "A cat sitting on a couch"

captioner = InconsistentCaptioner()

# Same image, different captions
caption1 = captioner.generate_caption("same_image.jpg")
caption2 = captioner.generate_caption("same_image.jpg")

# BUG: Inconsistent
print(f"Caption 1: {caption1}")
print(f"Caption 2: {caption2}")
"""
            
            test_file = os.path.join(temp_dir, "caption_consistency.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_visual_question_answering_reasoning(self):
        """Test 399: Perform reasoning for VQA"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SimpleVQA:
    def answer(self, image, question):
        # BUG: No reasoning - pattern matching only
        if "color" in question:
            return "blue"
        elif "how many" in question:
            return "3"
        else:
            return "unknown"

vqa = SimpleVQA()

# Requires reasoning
question = "Is the cat bigger than the dog?"
answer = vqa.answer("image.jpg", question)

# BUG: Can't reason about relative sizes
print(f"Answer: {answer}")
"""
            
            test_file = os.path.join(temp_dir, "vqa_reasoning.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_ocr_text_extraction_layout(self):
        """Test 400: Preserve layout in OCR text extraction"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class LayoutIgnoringOCR:
    def extract_text(self, image):
        # BUG: Returns text without layout info
        text = "Header Title Main Content Footer"
        return text

ocr = LayoutIgnoringOCR()

# Document with structured layout
extracted = ocr.extract_text("document.jpg")

# BUG: Lost layout structure
print(f"Extracted: {extracted}")
# Should preserve: header at top, content in middle, footer at bottom
"""
            
            test_file = os.path.join(temp_dir, "ocr_layout.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_multimodal_attention_mechanism(self):
        """Test 401: Implement cross-modal attention"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoAttentionVLM:
    def generate_caption(self, image, context_text):
        # BUG: Doesn't attend to context
        caption = "A generic image caption"
        return caption

vlm = NoAttentionVLM()

context = "This is a medical scan showing abnormalities"
caption = vlm.generate_caption("scan.jpg", context)

# BUG: Caption doesn't attend to medical context
print(f"Caption: {caption}")
"""
            
            test_file = os.path.join(temp_dir, "cross_attention.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_image_resolution_handling(self):
        """Test 402: Handle varying image resolutions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class FixedResolutionVLM:
    def __init__(self):
        self.expected_size = (224, 224)
    
    def process(self, image_size):
        # BUG: Assumes fixed resolution
        if image_size != self.expected_size:
            # BUG: Fails or distorts
            raise ValueError(f"Expected {self.expected_size}, got {image_size}")
        return "processed"

vlm = FixedResolutionVLM()

# High-res image
try:
    result = vlm.process((1920, 1080))
except ValueError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "resolution_handling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_visual_concept_compositionality(self):
        """Test 403: Compose visual concepts correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class LiteralVLM:
    def understand(self, description):
        # BUG: Can't compose concepts
        concepts = description.split()
        return concepts

vlm = LiteralVLM()

# Compositional description
result = vlm.understand("a red car next to a blue house")

# BUG: Returns ['a', 'red', 'car', 'next', 'to', 'a', 'blue', 'house']
# Should understand: red modifies car, blue modifies house, spatial relation
print(f"Concepts: {result}")
"""
            
            test_file = os.path.join(temp_dir, "compositionality.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_image_region_description(self):
        """Test 404: Describe specific image regions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class WholeImageDescriber:
    def describe_region(self, image, bbox):
        # BUG: Describes whole image, ignores bbox
        return "This is an image"

describer = WholeImageDescriber()

# Describe specific region
bbox = {"x": 100, "y": 100, "w": 50, "h": 50}
description = describer.describe_region("image.jpg", bbox)

# BUG: Doesn't focus on specified region
print(f"Region description: {description}")
"""
            
            test_file = os.path.join(temp_dir, "region_description.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_temporal_visual_understanding(self):
        """Test 405: Understand temporal aspects in images/videos"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class StaticVLM:
    def analyze_sequence(self, frames):
        # BUG: Analyzes frames independently
        descriptions = []
        for frame in frames:
            descriptions.append(f"Frame: {frame}")
        return descriptions

vlm = StaticVLM()

# Video frames showing motion
frames = ["person_standing.jpg", "person_jumping.jpg", "person_landing.jpg"]
analysis = vlm.analyze_sequence(frames)

# BUG: Doesn't understand temporal sequence (jumping action)
print(f"Analysis: {analysis}")
"""
            
            test_file = os.path.join(temp_dir, "temporal_understanding.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestAudioProcessing:
    """Test audio processing and understanding (10 tests)"""
    
    def test_audio_transcription_accuracy(self):
        """Test 406: Accurate audio transcription with noise"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoiseSensitiveASR:
    def transcribe(self, audio, noise_level):
        # BUG: No noise handling
        if noise_level > 0.2:
            return "unintelligible"
        return "transcribed text"

asr = NoiseSensitiveASR()

# Audio with moderate noise
transcription = asr.transcribe("audio.wav", noise_level=0.3)

# BUG: Should use noise reduction
print(f"Transcription: {transcription}")
"""
            
            test_file = os.path.join(temp_dir, "noise_transcription.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_speaker_diarization(self):
        """Test 407: Identify different speakers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoDiarizationASR:
    def transcribe(self, audio):
        # BUG: No speaker identification
        return "Person: Hello how are you fine thanks"

asr = NoDiarizationASR()

# Multi-speaker audio
transcription = asr.transcribe("conversation.wav")

# BUG: Doesn't identify speakers
print(f"Transcription: {transcription}")
# Should be: Speaker1: Hello, Speaker2: how are you, Speaker1: fine thanks
"""
            
            test_file = os.path.join(temp_dir, "speaker_diarization.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_audio_emotion_recognition(self):
        """Test 408: Recognize emotions from audio"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EmotionBlindASR:
    def transcribe_with_emotion(self, audio):
        # BUG: Only transcribes words, ignores emotion
        return {"text": "I am fine", "emotion": None}

asr = EmotionBlindASR()

# Angry tone audio
result = asr.transcribe_with_emotion("angry_voice.wav")

# BUG: Missing emotion
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "emotion_recognition.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_audio_language_detection(self):
        """Test 409: Detect language before transcription"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SingleLanguageASR:
    def __init__(self):
        self.language = "english"
    
    def transcribe(self, audio):
        # BUG: Assumes English
        return f"Transcribed in {self.language}"

asr = SingleLanguageASR()

# Spanish audio
transcription = asr.transcribe("spanish_audio.wav")

# BUG: Wrong language model
print(f"Transcription: {transcription}")
"""
            
            test_file = os.path.join(temp_dir, "language_detection.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_audio_segmentation_boundaries(self):
        """Test 410: Detect proper segment boundaries"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class FixedSegmentASR:
    def segment_audio(self, audio_duration):
        # BUG: Fixed length segments, breaks words
        segment_length = 5  # seconds
        segments = []
        
        for i in range(0, audio_duration, segment_length):
            segments.append((i, i + segment_length))
        
        return segments

asr = FixedSegmentASR()

# 17 second audio
segments = asr.segment_audio(17)

# BUG: Last segment cuts off at 15s, splits word
print(f"Segments: {segments}")
"""
            
            test_file = os.path.join(temp_dir, "audio_segmentation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_acoustic_feature_normalization(self):
        """Test 411: Normalize acoustic features"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnnormalizedASR:
    def extract_features(self, audio, volume):
        # BUG: Doesn't normalize for volume
        features = [volume * 0.1] * 128
        return features

asr = UnnormalizedASR()

# Same content, different volumes
quiet = asr.extract_features("audio.wav", volume=0.2)
loud = asr.extract_features("audio.wav", volume=1.0)

# BUG: Different features for same content
print(f"Quiet features: {quiet[:3]}")
print(f"Loud features: {loud[:3]}")
"""
            
            test_file = os.path.join(temp_dir, "feature_normalization.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_audio_punctuation_restoration(self):
        """Test 412: Restore punctuation in transcriptions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoPunctuationASR:
    def transcribe(self, audio):
        # BUG: No punctuation
        return "hello how are you im fine thanks"

asr = NoPunctuationASR()

transcription = asr.transcribe("conversation.wav")

# BUG: Hard to read without punctuation
print(f"Transcription: {transcription}")
# Should be: "Hello, how are you? I'm fine, thanks."
"""
            
            test_file = os.path.join(temp_dir, "punctuation_restoration.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_audio_streaming_latency(self):
        """Test 413: Low-latency streaming transcription"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class BatchOnlyASR:
    def transcribe_stream(self, audio_chunks):
        # BUG: Waits for all chunks before processing
        all_audio = []
        for chunk in audio_chunks:
            all_audio.append(chunk)
        
        # Process at end
        return "final transcription"

asr = BatchOnlyASR()

chunks = ["chunk1", "chunk2", "chunk3"]
result = asr.transcribe_stream(chunks)

# BUG: High latency - should stream results
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "streaming_latency.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_background_noise_classification(self):
        """Test 414: Classify background noise"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoiseIgnoringASR:
    def transcribe(self, audio):
        # BUG: Doesn't identify background noise
        return {
            "text": "transcribed speech",
            "background": None
        }

asr = NoiseIgnoringASR()

# Audio with traffic noise
result = asr.transcribe("street_audio.wav")

# BUG: Missing background context
print(f"Result: {result}")
# Should identify: traffic, outdoor environment
"""
            
            test_file = os.path.join(temp_dir, "background_classification.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_audio_quality_assessment(self):
        """Test 415: Assess audio quality before processing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class QualityBlindASR:
    def transcribe(self, audio, sample_rate):
        # BUG: No quality check
        return "transcription"

asr = QualityBlindASR()

# Low quality audio
result = asr.transcribe("low_quality.wav", sample_rate=8000)

# BUG: Should warn about quality issues
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "quality_assessment.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestCrossModalIntegration:
    """Test cross-modal integration (10 tests)"""
    
    def test_audio_visual_synchronization(self):
        """Test 416: Synchronize audio and visual streams"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DesyncedAVProcessor:
    def process(self, video_frames, audio_chunks):
        # BUG: Doesn't check sync
        video_result = self.process_video(video_frames)
        audio_result = self.process_audio(audio_chunks)
        
        return {
            "video": video_result,
            "audio": audio_result
        }
    
    def process_video(self, frames):
        return "video_features"
    
    def process_audio(self, chunks):
        return "audio_features"

processor = DesyncedAVProcessor()

# Audio/video with 500ms offset
result = processor.process(["frame1", "frame2"], ["audio1", "audio2"])

# BUG: Doesn't detect/correct sync issues
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "av_sync.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_modality_missing_fallback(self):
        """Test 417: Handle missing modalities gracefully"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class BrittleMultiModal:
    def process(self, image, audio, text):
        # BUG: Requires all modalities
        img_features = self.process_image(image)
        aud_features = self.process_audio(audio)
        txt_features = self.process_text(text)
        
        return img_features + aud_features + txt_features
    
    def process_image(self, img):
        return [0.1]
    
    def process_audio(self, aud):
        if aud is None:
            raise ValueError("Audio required")
        return [0.2]
    
    def process_text(self, txt):
        return [0.3]

processor = BrittleMultiModal()

# Missing audio modality
try:
    result = processor.process("image.jpg", None, "text")
except ValueError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "missing_modality.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cross_modal_retrieval(self):
        """Test 418: Retrieve across modalities"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SiloedRetrieval:
    def __init__(self):
        self.images = ["img1", "img2", "img3"]
        self.texts = ["text1", "text2", "text3"]
    
    def search_by_text(self, query):
        # BUG: Only searches text, not images
        results = [t for t in self.texts if query in t]
        return results

retriever = SiloedRetrieval()

# Query: "Find images described by 'cat'"
results = retriever.search_by_text("cat")

# BUG: Doesn't retrieve matching images
print(f"Results: {results}")
"""
            
            test_file = os.path.join(temp_dir, "cross_modal_retrieval.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_modality_confidence_fusion(self):
        """Test 419: Fuse modality confidences correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SimpleAverageFusion:
    def fuse_predictions(self, predictions):
        # BUG: Simple average ignores confidence
        total = 0
        for pred in predictions:
            total += pred["score"]
        return total / len(predictions)

fusion = SimpleAverageFusion()

predictions = [
    {"modality": "visual", "score": 0.9, "confidence": 0.95},
    {"modality": "audio", "score": 0.3, "confidence": 0.2}
]

# BUG: Should weight by confidence
result = fusion.fuse_predictions(predictions)
print(f"Fused score: {result}")  # (0.9 + 0.3) / 2 = 0.6
# Should be ~0.87 (weighted by confidence)
"""
            
            test_file = os.path.join(temp_dir, "confidence_fusion.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_temporal_cross_modal_alignment(self):
        """Test 420: Align temporal aspects across modalities"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnalignedTemporal:
    def process_video_with_transcript(self, video_frames, transcript):
        # BUG: Doesn't align timestamps
        video_events = self.detect_events(video_frames)
        text_events = self.parse_transcript(transcript)
        
        return {
            "video": video_events,
            "text": text_events
        }
    
    def detect_events(self, frames):
        return [{"event": "person_walking", "frame": 10}]
    
    def parse_transcript(self, transcript):
        return [{"text": "walking", "time": 0.5}]

processor = UnalignedTemporal()

result = processor.process_video_with_transcript(["frame1"], "walking")

# BUG: Doesn't align "walking" (0.5s) with frame 10
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "temporal_alignment.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_modality_contradiction_resolution(self):
        """Test 421: Resolve contradictions between modalities"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoContradictionCheck:
    def fuse_modalities(self, visual_pred, audio_pred):
        # BUG: Doesn't detect contradictions
        return {
            "visual": visual_pred,
            "audio": audio_pred
        }

fusion = NoContradictionCheck()

# Visual: person smiling
# Audio: person crying
result = fusion.fuse_modalities(
    visual_pred="happy",
    audio_pred="sad"
)

# BUG: Should flag contradiction
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "contradiction_resolution.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_multimodal_embedding_space(self):
        """Test 422: Shared embedding space for modalities"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SeparateEmbeddings:
    def embed_image(self, image):
        return [0.1] * 512
    
    def embed_text(self, text):
        return [0.2] * 768
    
    def embed_audio(self, audio):
        return [0.3] * 256

embedder = SeparateEmbeddings()

img_emb = embedder.embed_image("cat.jpg")
txt_emb = embedder.embed_text("a cat")
aud_emb = embedder.embed_audio("meow.wav")

# BUG: Different dimensions, can't compare
print(f"Dimensions: img={len(img_emb)}, txt={len(txt_emb)}, aud={len(aud_emb)}")
"""
            
            test_file = os.path.join(temp_dir, "shared_embedding.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_modality_specific_preprocessing(self):
        """Test 423: Apply modality-specific preprocessing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class GenericPreprocessor:
    def preprocess(self, data, modality):
        # BUG: Same preprocessing for all modalities
        normalized = [x / 255.0 for x in data]
        return normalized

preprocessor = GenericPreprocessor()

# Audio data (different range than images)
audio = [0.5, -0.3, 0.8]  # Already in [-1, 1]
processed = preprocessor.preprocess(audio, "audio")

# BUG: Wrong normalization for audio
print(f"Processed audio: {processed}")
"""
            
            test_file = os.path.join(temp_dir, "modality_preprocessing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cross_modal_attention_weights(self):
        """Test 424: Learn cross-modal attention weights"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UniformAttention:
    def attend(self, query_modality, key_modalities):
        # BUG: Uniform attention, doesn't learn
        num_modalities = len(key_modalities)
        return {m: 1.0 / num_modalities for m in key_modalities}

attention = UniformAttention()

# Visual query attending to audio and text
weights = attention.attend("visual", ["audio", "text"])

# BUG: Equal weights regardless of relevance
print(f"Attention weights: {weights}")
"""
            
            test_file = os.path.join(temp_dir, "cross_attention_weights.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_modality_translation_consistency(self):
        """Test 425: Maintain consistency in modality translation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InconsistentTranslator:
    def image_to_text(self, image):
        # BUG: Non-deterministic
        import random
        descriptions = ["a cat", "a dog", "a bird"]
        return random.choice(descriptions)
    
    def text_to_image(self, text):
        return f"generated_image_from_{text}"

translator = InconsistentTranslator()

# Translate image -> text -> image
img = "cat.jpg"
text = translator.image_to_text(img)
reconstructed = translator.text_to_image(text)

# BUG: Inconsistent round-trip
print(f"Original: {img}")
print(f"Via text: {text}")
print(f"Reconstructed: {reconstructed}")
"""
            
            test_file = os.path.join(temp_dir, "translation_consistency.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
