ALL-IN-ONE AI PHOTO STUDIO — SETUP

Files:
- index.html: Blogger/static frontend
- main.py: FastAPI API (open-source U2Net background remover)
- requirements.txt: Python dependencies
- render.yaml: Render deployment setup

Deploy API:
1. GitHub पर नया repository बनाएँ और main.py, requirements.txt, render.yaml root में upload करें.
2. Render.com में New > Blueprint चुनकर repository connect करें और deploy करें.
3. Service URL के root पर {"status":"ok"...} दिखना चाहिए.
4. index.html में API_BASE की value को अपने Render URL से बदलें.
5. Blogger के HTML view में index.html का code paste करके publish करें. यदि Blogger scripts/style strip करे, static hosting पर index.html रखें और Blogger से link करें.

Notes:
- किसी paid API key की जरूरत नहीं; rembg/U2Net open-source model है.
- Free hosting sleep/cold-start कर सकती है और पहली model request में देरी होगी.
- Enhance endpoint में upscaling/sharpening है, generative face restoration नहीं.
- Demo API public है; production में CORS को अपने domain तक सीमित करें और authentication/rate limit जोड़ें. संवेदनशील फोटो public server पर upload न करें.
- Print dialog में A4, 100% scale चुनें और browser headers/footers बंद करें.
