# Security Policy

## Project: Tiny Me purrGpt

Tiny Me is designed to be a local, privacy-friendly AI chatbot.  
We take security and user privacy seriously — please review the following guidelines before reporting issues or vulnerabilities.

---

## Reporting a Vulnerability

If you discover a security issue, please **do not open a public issue**.

Instead, contact us directly at:

> 📧 **randomcatuser@proton.me**

Provide a clear description of the problem, including:
- Steps to reproduce the issue
- Possible impact or data affected
- Suggested fixes or mitigation (if any)

We will acknowledge your report within **48 hours** and provide a fix or response within **7–10 days**.

---

## Supported Versions

We actively maintain the most recent **main branch** only.

| Version | Supported | Notes |
|----------|------------|--------|
| main (latest) | ✅ Yes | Actively maintained |
| older versions | ❌ No | Use the latest for security patches |

---

## Data & Privacy

- No personal data is sent to any third-party servers except **Pollinations API** for AI text generation.  
- Local memory (chat history) is stored only in your browser’s `localStorage` within the PyQt environment.  
- Clearing memory removes all stored data permanently.  
- The app does **not** collect analytics, telemetry, or external logs.

---

## Safe Usage Tips

- Avoid entering private, financial, or sensitive data into the chatbot.  
- Always verify API endpoints and source code before connecting to third-party services.  
- Keep your Python environment and dependencies up to date.

---

## Responsible Disclosure

We encourage ethical security research and responsible disclosure.  
If your finding results in a confirmed vulnerability, we’ll credit you in the project’s contributors list (if you wish).

---

## Future Security Enhancements

- Optional encryption for localStorage memory  
- User-level permissions and sandboxing  

---

> **Thank you** for helping us keep Tiny Me purrGpt safe, private, and trustworthy.
