# Media migration

Images are local WebP files, fitted within 1600 x 1600 without cropping. The Going Green article screenshot retains its original resolution for legibility.

Original YouTube videos remain external embeds with locally stored thumbnails. Their availability and embedding permissions remain controlled by the original publishers.

Wix-hosted public MP4 and MP3 media are downloaded locally, so they do not require the old Wix website to remain live.

Going Green contains an article JPEG and a YouTube link, with no PDF or document attachment exposed in the public article markup.

Downloaded 121 assets (74.5 MB). Extracted 43 media components.

The asset set contains 116 images, three MP4 videos, one MP3 audio file and one linked research PDF. The original site contains no Going Green PDF: that article is represented by a full-resolution JPEG, converted to a full-resolution WebP.

The LAB videos required refreshing the normal anonymous public-player session and remuxing the public 720p HLS streams to MP4. Playback tokens are not persisted in the manifest or media files.

Validation: every local asset exists and is nonempty; every WebP passed Pillow image verification. FFmpeg decoded the first second of each MP4 and MP3 successfully. Durations are 30.89 s (KFC), 144.84 s (KCL Cassettes), 92.37 s (Lynk), and 84.36 s (JPS).

Portfolio media component mapping:

- `comp-mmj3i3bn`: A love for the land, YouTube `9SjVzjYOx_8`.
- `comp-mrkgpjqt`: The restorative power of nature, YouTube `6wny1zoYYkI`.
- `comp-kyubdibn`: Dennis Brown documentary, YouTube `TPhNr8iqHxk`.
- `comp-kyucasy5`: KFC Jamaica commercial, local MP4.
- `comp-jyu5tm8n`: Cycling vlog, YouTube `37IPSdi7AtM`.
- `comp-jt1s5c3k`: KCL Cassettes, local MP3.
- `comp-md1qaf9s`: Six film production / workshop gallery images.
- `comp-kyucrde9`: Six LAB production gallery images.
- `comp-jytzh38v`: All 14 Student LifeStart gallery images.
- `comp-jyu50cy5`: Both mobile journalism videos (To Fly Or Not To Fly? and A Short Guide to Beirut).
- `comp-kyubpcpj`: All eight LAB video-channel entries, including both locally migrated Wix videos.
