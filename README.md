# 🚀 Auto Job Apply — Setup Guide (Mac, Beginner Friendly)

## What's in this folder?

| File | What it does |
|---|---|
| `config.py` | **Your settings** — fill this in first! |
| `linkedin_apply.py` | Auto-applies on LinkedIn Easy Apply |
| `stepstone_apply.py` | Auto-applies on StepStone.de |
| `README.md` | This guide |

---

## ✅ Step 1 — Install Python (if not done yet)

1. Go to https://www.python.org/downloads/
2. Download & install Python 3
3. Open **Terminal** (Cmd + Space → type Terminal → Enter)
4. Confirm it works:
   ```
   python3 --version
   ```

---

## ✅ Step 2 — Install required packages

In Terminal, run:
```bash
pip3 install selenium webdriver-manager
```

---

## ✅ Step 3 — Fill in your details in `config.py`

Open `config.py` in any text editor (TextEdit, VS Code, etc.) and fill in:

- ✏️ Your LinkedIn and StepStone **email + password**
- ✏️ Your **name, phone, city**
- ✏️ The **full path to your CV** (PDF recommended)
  - Example: `/Users/john/Documents/John_CV.pdf`
- ✏️ Adjust `MAX_APPLIES` (default: 20 per run)

---

## ✅ Step 4 — Put all files in one folder

Create a folder on your Desktop called `job-apply` and put all 4 files inside it.

---

## ✅ Step 5 — Run the scripts

Open Terminal and navigate to your folder:
```bash
cd ~/Desktop/job-apply
```

### Run LinkedIn auto-apply:
```bash
python3 linkedin_apply.py
```

### Run StepStone auto-apply:
```bash
python3 stepstone_apply.py
```

A Chrome browser window will open automatically. **Don't close it** — let the script work!

---

## ⚠️ Important Tips

- **Watch the browser** the first time to make sure everything looks right
- If LinkedIn asks for a **CAPTCHA or verification**, complete it manually and the script will continue
- Start with `MAX_APPLIES = 5` to test before increasing
- LinkedIn may **temporarily limit applications** if you apply too fast — the script has built-in random delays to avoid this
- Keep your **CV file path correct** — if the path is wrong, CV upload will be skipped
- StepStone applications vary by employer — some will go fully automatic, some will open company career pages

---

## 🛑 To Stop the Script

Press `Ctrl + C` in Terminal at any time.

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip3 install selenium webdriver-manager` again |
| Chrome doesn't open | Make sure Google Chrome is installed on your Mac |
| Login fails | Double-check email/password in `config.py` |
| CV not uploading | Check the full file path in `config.py` — no typos! |
| Script stops unexpectedly | LinkedIn may have changed its HTML — try again later or raise an issue |

---

## 📌 Recommended Workflow

1. Run with `MAX_APPLIES = 5` first to test
2. Review the jobs it applied to
3. If happy, increase to 20–30 per day
4. Run once in the morning and once in the evening
5. Check your email for responses!

Good luck with your job search! 🍀
# job-apply
