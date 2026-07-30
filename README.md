# kadam-models

Версионированные модели кыргызской речи для мобильного приложения `altyntil`.
Весовые файлы распространяются через Git LFS и должны публиковаться как GitHub
Release assets. Они не должны добавляться в Flutter assets и не входят в APK,
AAB или IPA.

## Состав

- `tts/model.onnx` — Meta MMS `facebook/mms-tts-kir`, готовый ONNX из
  `willwade/mms-tts-multilingual-models-onnx/kir`.
- `tts/tokens.txt` — таблица символов MMS из того же набора.
- `asr/model.onnx` — MatMul INT8-экспорт
  `iarfmoose/wav2vec2-large-xlsr-kyrgyz`, созданный штатным
  `app/scripts/export-asr.py` проекта Kadam.
- `asr/vocab.json` и `asr/asr-meta.json` — словарь CTC и параметры
  препроцессинга, полученные тем же экспортом.

В исходном Kadam ASR-модель фактически находится как `app/models/model.onnx`,
а метаданные — в `app/models/`; здесь они намеренно сгруппированы под `asr/`.
Используются только эти пять runtime-файлов — сервер, Python-окружение,
исходный FP32 ONNX и web-приложение не включены.

## Контракт inference

TTS принимает:

- `x`: `int64[1, sequence]`;
- `x_length`: `int64[1]`;
- `noise_scale`: `float32[1]`, Kadam использует `0.667`;
- `length_scale`: `float32[1]`, Kadam использует `1.0`;
- `noise_scale_w`: `float32[1]`, Kadam использует `0.8`.

Первый output TTS — mono `float32` waveform с частотой 16 kHz. Токенизация
посимвольная: неизвестные символы пропускаются, поддерживается lowercase
fallback, blank `0` вставляется до, после и между token id.

ASR принимает `input_values: float32[batch,time]` и возвращает
`logits: float32[batch,frames,vocab]`. Аудио: mono 16 kHz, значения
`[-1, 1]`, затем zero-mean/unit-variance нормализация с epsilon `1e-7`.
Greedy CTC decoder удаляет повторы и blank/pad id `39`, заменяет `|` пробелом
и отбрасывает специальные токены.

## Обновление manifest

После замены любого файла:

```bash
python3 scripts/update_manifest.py
```

После создания GitHub Release рекомендуется загрузить assets с именами
`tts-model.onnx`, `tts-tokens.txt`, `asr-model.onnx`, `asr-vocab.json`,
`asr-asr-meta.json`, затем закрепить URL:

```bash
python3 scripts/update_manifest.py \
  --base-url https://github.com/OWNER/kadam-models/releases/download/v1.0.0
```

Сам `manifest.json` публикуйте по неизменяемому тегу:

`https://raw.githubusercontent.com/OWNER/kadam-models/v1.0.0/manifest.json`

## Публикация

```bash
git init
git branch -M main
git lfs install
git lfs track "*.onnx"
git add .gitattributes .gitignore README.md manifest.json scripts tts asr
git commit -m "Initial speech models release"
git remote add origin git@github.com:OWNER/kadam-models.git
git push -u origin main
git tag -a v1.0.0 -m "Speech models v1.0.0"
git push origin v1.0.0
```

Создание публичного репозитория и Release выполняется владельцем GitHub.
