# CLP Customer Loyalty Mobile Application – Verification & Test Report

**Target Mobile Application:** CLP Customer Loyalty Program (Android)  
**App Version:** 1.1.0  
**Package Identifier:** `com.hiideals.clp`  
**Framework:** Expo SDK 52 + React Native 0.76 + TypeScript  
**Build Artifact:** `CLP_Mobile_App_Fixed_v1.1.apk` (85.81 MB / 85,810,937 bytes)  
**Artifact Location:** `E:\clp updated code\clp-mobile-app\CLP_Mobile_App_Fixed_v1.1.apk`  
**Configured Production Backend:** `https://clp.hiideals.com`  
**Date:** November 10, 2026  

---

## 1. Application Build & Configuration Audit

| Configuration Component | Configured Value | Verification Method | Status |
| :--- | :--- | :--- | :---: |
| **API Base URL** | `https://clp.hiideals.com` | `api.ts` / `app.json` inspection | **VERIFIED** |
| **Application Icon** | `assets/images/clp-app-icon.png` (Official CLP Branding) | Asset check & dimensions inspection | **VERIFIED** |
| **Android Adaptive Icon** | `foregroundImage: ./assets/images/clp-app-icon.png`, `backgroundColor: #0f172a` | `app.json` adaptive icon configuration | **VERIFIED** |
| **Splash Screen** | Official CLP splash screen | `assets/splash.png` | **VERIFIED** |
| **Permissions** | `CAMERA` (for QR scanning), `INTERNET`, `ACCESS_NETWORK_STATE` | `AndroidManifest.xml` / `app.json` | **VERIFIED** |
| **Secure Token Storage** | `expo-secure-store` | Session persistence service | **VERIFIED** |

---

## 2. Mobile Feature Test Matrix

| # | Mobile Workflow | Expected Behavior | Actual Behavior | Status |
| :---: | :--- | :--- | :--- | :---: |
| **1** | **App Launch & Splash** | App launches with official branding and transitions smoothly to Login. | Launches cleanly with splash animation. | **PASSED** |
| **2** | **Staff Authentication** | Attendant enters credentials; app authenticates with Frappe `/api/method/login`. | Session cookie & token stored securely in `SecureStore`. | **PASSED** |
| **3** | **Session Persistence** | Closing and reopening the app keeps the attendant logged in. | Attendant directly enters the dashboard without re-entering credentials. | **PASSED** |
| **4** | **QR Scanner Integration** | Camera opens, scans customer QR code (`?token=...` or legacy ID), resolves customer. | Successfully parses query parameters and loads customer card. | **PASSED** |
| **5** | **Customer Search** | Attendant searches by vehicle, phone, or name. Spaced vehicle numbers trigger guidance. | Fast search results displayed; continuous format enforced. | **PASSED** |
| **6** | **New Customer Registration** | Attendant registers customer with mandatory petrol pump and space-free vehicle. | Validated locally and registered via `/api/method/frappe.client.insert`. | **PASSED** |
| **7** | **Fuel Purchase Submission** | Attendant enters refuel liters and taps "Save & Submit". Anti-double click active. | Attendant screen hides `amount` & `fuel_type`; single transaction recorded. | **PASSED** |
| **8** | **Gift Redemption Workflow** | Attendant selects gift item, verifies points, and submits redemption. | Points deducted, ERPNext stock entry triggered, instant confirmation. | **PASSED** |
| **9** | **Profile Update** | Customer or staff updates name or continuous vehicle number. | Calls `clp.api.update_customer_profile` with valid token. | **PASSED** |
| **10** | **Network Error Handling** | Network disconnect triggers user-friendly offline toast without crash. | Offline state handled gracefully with retry option. | **PASSED** |
| **11** | **Logout & Session Clear** | Attendant logs out; `SecureStore` tokens cleared. | Returns to clean login screen; previous session revoked. | **PASSED** |

---

## 3. Installation Instructions

To install the verified v1.1.0 build on Android devices:

```bash
# 1. Connect Android device via USB with USB Debugging enabled
adb devices

# 2. Install the standalone APK directly
adb install -r "E:\clp updated code\clp-mobile-app\CLP_Mobile_App_Fixed_v1.1.apk"

# 3. Alternatively, copy the APK to the phone storage and tap to install.
```

---

## 4. Mobile Application Verdict

The CLP Mobile Application v1.1.0 is production-ready. It connects to `https://clp.hiideals.com`, features official CLP branding, persists authentication securely, and executes all attendant workflows reliably.
