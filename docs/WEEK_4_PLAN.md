# Week 4 Action Plan - Audio Generation

**Goal**: Implement the core audio engine to generate voice narration from text, combine audio files, and format them for consumption.

---

## 🎯 This Week's Objectives

1.  Implement `AudioGenerator` to convert text chunks to AIFF using the system TTS (`say` command).
2.  Implement `AudioCombiner` to merge chunked AIFF lines into complete chapter tracks.
3.  Implement `AudioConverter` to transcribe AIFF audio into final formats (MP3, M4B).
4.  Achieve 80%+ test coverage.

---

## 📋 Day-by-Day Breakdown

### Day 1: Audio Generator
**Tasks**:
1.  Create `app/audio/generator.py`:
    -   Class `AudioGenerator`.
    -   Method `generate_chunk(text, output_file)`: Wraps `subprocess.run(["say", ...])`.
    -   Support for configuring Voice andRate.
    -   Async support (maybe?) or just parallel processing with `concurrent.futures`.
2.  Write tests `tests/unit/test_audio_generator.py`:
    -   Mock `subprocess.run` to verify commands without actually speaking.

**Deliverable**: Python class that can make your computer speak text to a file.

---

### Day 2: Audio Combiner (SoX Integration)
**Tasks**:
1.  Create `app/audio/combiner.py`:
    -   Class `AudioCombiner`.
    -   Method `combine(input_files, output_file)`: Wraps `subprocess.run(["sox", ...])`.
    -   Concatenates multiple AIFF files into one chapter file.
2.  Write tests `tests/unit/test_audio_combiner.py`.

**Deliverable**: Ability to merge small audio chunks into a full chapter.

---

### Day 3: Audio Converter (FFmpeg Integration)
**Tasks**:
1.  Create `app/audio/converter.py`:
    -   Class `AudioConverter`.
    -   Method `to_mp3(input, output)`: converting simple files.
    -   Method `to_m4b(inputs, output)`: complex combining with chapter marks (maybe start simple first).
2.  Write tests `tests/unit/test_audio_converter.py`.

**Deliverable**: Producing the final MP3 files.

---

### Day 4: Batch Processing & Job Management
**Tasks**:
1.  Connect the dots in `app/app.py`:
    -   For each chapter in `document`:
        -   Chunk text (by sentences/lines).
        -   Generate audio for each chunk.
        -   Combine chunks.
        -   Convert to MP3.
2.  Update `AudioJob` model in DB to track progress.

**Deliverable**: End-to-end flow from Text -> MP3.

---

### Day 5: Refinement & Testing
**Tasks**:
1.  Full integration test.
2.  Check performance (parallel generation?).
3.  Cleanup temporary files (crucial! AIFFs get huge).

---

## 🏗️ File Structure Updates

```
audio-creator/
├── app/
│   ├── audio/
│   │   ├── __init__.py          ✅ NEW
│   │   ├── generator.py         ✅ NEW
│   │   ├── combiner.py          ✅ NEW
│   │   └── converter.py         ✅ NEW
├── tests/
│   ├── unit/
│   │   ├── test_audio_generator.py ✅ NEW
│   │   ├── test_audio_combiner.py  ✅ NEW
│   │   └── test_audio_converter.py ✅ NEW
```

---

## ⚠️ Common Pitfalls

1.  **Disk Usage**: AIFF files are uncompressed. Generating a whole book at once might eat gigabytes. Process chapter-by-chapter and clean up!
2.  **Subprocess Calls**: Ensure arguments are safely escaped.
3.  **Concurrency**: The `say` command might not like being called 20 times in parallel on the same machine. Measure safe limits.

---

## 🎯 Success Criteria for Week 4

-   [ ] Run `python -m app.app story.txt --voice Alex` and get a `story.mp3`.
-   [ ] Intermediate AIFF files are deleted automatically.
-   [ ] Supports custom voices and speed.
