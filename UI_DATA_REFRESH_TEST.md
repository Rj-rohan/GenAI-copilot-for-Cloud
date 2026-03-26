# UI Data Refresh Test Guide

## Problem
You're seeing the same data in the UI even after generating new data.

## Root Cause
Browser caching + the need to manually refresh after generation.

## Solution - 3 Ways to See New Data

### Method 1: Use the "Generate Data" Button in UI ✅ RECOMMENDED

1. Open the UI: `http://localhost:5173`
2. Click the **"⟳ Generate Data"** button in the top-right
3. Wait for the success message
4. Data will automatically refresh!

**This is the BEST way** - it generates new data AND refreshes automatically.

---

### Method 2: Hard Refresh Browser

After generating data via command line:

**Windows/Linux:**
- Press `Ctrl + Shift + R` or `Ctrl + F5`

**Mac:**
- Press `Cmd + Shift + R`

This clears the browser cache and loads fresh data.

---

### Method 3: Clear Browser Cache

1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

---

## Test to Verify Data is Changing

### Step 1: Note Current Data
```bash
# Open UI and note:
- Total findings count
- Top risk score
- Critical count
```

### Step 2: Generate New Data
```bash
cd backend
python generate_data_multicloud.py --provider aws --count 10
copy data\findings_aws.json ..\frontend\public\findings_aws.json
```

### Step 3: Check Backend File
```bash
# Open the file and check the top risk score
notepad ..\frontend\public\findings_aws.json
```

Look for the first `"risk_score"` value - it should be DIFFERENT from before.

### Step 4: Hard Refresh Browser
Press `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)

### Step 5: Verify UI Updated
The numbers should now match the backend file!

---

## Quick Verification Script

Run this to see if data is actually changing:

```bash
# Generate data 3 times and show top risk scores
cd backend

echo "Run 1:"
python generate_data_multicloud.py --provider aws --count 5
findstr /C:"risk_score" data\findings_aws.json | findstr /N "." | findstr "^2:"

echo "Run 2:"
python generate_data_multicloud.py --provider aws --count 5
findstr /C:"risk_score" data\findings_aws.json | findstr /N "." | findstr "^2:"

echo "Run 3:"
python generate_data_multicloud.py --provider aws --count 5
findstr /C:"risk_score" data\findings_aws.json | findstr /N "." | findstr "^2:"
```

You should see 3 DIFFERENT risk scores!

---

## Why This Happens

1. **Browser Cache**: Browsers cache JSON files for performance
2. **Service Workers**: Vite dev server might cache responses
3. **React State**: The component needs to re-fetch data

## The Fix

The `?t=${Date.now()}` in the code should prevent caching, but browsers are aggressive. Always do a **hard refresh** after generating new data via command line.

**OR** just use the **"Generate Data" button in the UI** - it handles everything automatically!

---

## Proof Data is Different

Run this command twice:

```bash
# First run
python generate_data_multicloud.py --provider aws --count 5 > output1.txt

# Second run  
python generate_data_multicloud.py --provider aws --count 5 > output2.txt

# Compare
fc output1.txt output2.txt
```

You'll see the outputs are DIFFERENT - proving the data generator works correctly.

The issue is just getting the browser to load the new file!
