"""
Selenium UI Automation Script - Google Search Demo
Demonstrates a Selenium UI test that can be scheduled via MindMap or executed standalone.
Supports both headless background execution and visible browser mode.
"""

import sys
import time
import argparse
import traceback

# Safe imports with helpful diagnostic messages
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ModuleNotFoundError as e:
    print(
        f"[ERROR] Required package missing: {e}\n"
        "To fix this, install selenium in your Python environment:\n"
        "    pip install selenium webdriver-manager\n"
        "Or make sure your virtual environment (.venv) is activated:\n"
        "    .\\.venv\\Scripts\\activate\n",
        file=sys.stderr,
        flush=True,
    )
    sys.exit(1)

# webdriver-manager is optional because Selenium 4.6+ has native Selenium Manager
try:
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_WEBDRIVER_MANAGER = True
except ImportError:
    HAS_WEBDRIVER_MANAGER = False


# ── Configuration Defaults ─────────────────────────────────
DEFAULT_SEARCH_QUERY = "MindMap automation tool"
TARGET_URL           = "https://www.google.com"
DEFAULT_HEADLESS     = False  # Set to True for silent background runs
DEFAULT_TIMEOUT      = 20     # seconds
DEFAULT_STEP_DELAY   = 2.0    # seconds to pause between steps


def _dismiss_consent(driver, wait):
    """Handle Google consent / cookie popup if present."""
    try:
        consent_selectors = [
            "button#L2AGLb",               # "Accept all" (English)
            "button[aria-label*='Accept']",
            "button[jsname='b3VHJd']",
            "button[aria-label*='Agree']",
        ]
        for sel in consent_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, sel)
                for btn in elements:
                    if btn.is_displayed():
                        btn.click()
                        print("[INFO]  Dismissed Google consent popup.", flush=True)
                        time.sleep(1)
                        return
            except NoSuchElementException:
                continue
    except Exception:
        pass  # Consent popup not found or not required


def _wait_for_results(driver, wait):
    """
    Wait for Google search results using multiple fallback selectors.
    Google's DOM varies by region and experiment; this checks several anchors.
    """
    result_selectors = [
        (By.ID,           "search"),                   # Classic container
        (By.ID,           "rso"),                      # Result set container
        (By.CSS_SELECTOR, "div.g"),                    # Result card
        (By.CSS_SELECTOR, "[data-sokoban-container]"),
        (By.CSS_SELECTOR, "h3"),                       # Heading inside any result
    ]
    for by, sel in result_selectors:
        try:
            wait.until(EC.presence_of_element_located((by, sel)))
            print(f"[INFO]  Results detected via selector: '{sel}'", flush=True)
            return True
        except TimeoutException:
            continue
    return False


def run(search_query=DEFAULT_SEARCH_QUERY, headless=DEFAULT_HEADLESS,
        step_delay=DEFAULT_STEP_DELAY, timeout=DEFAULT_TIMEOUT):
    """Execute the Selenium Google Search workflow."""
    print("[INFO] Starting Selenium script: Google Search Demo", flush=True)
    print(f"[INFO] Target URL  : {TARGET_URL}", flush=True)
    print(f"[INFO] Search term : {search_query}", flush=True)
    print(f"[INFO] Headless    : {headless}", flush=True)
    print(f"[INFO] Step Delay  : {step_delay}s", flush=True)
    print("-" * 50, flush=True)

    # ── Chrome options ─────────────────────────────────────
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")

    # Anti-bot detection measures
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    driver = None
    try:
        # ── Launch browser ─────────────────────────────────────
        print("[STEP 1] Launching Chrome browser...", flush=True)
        try:
            # 1. Prefer modern Selenium 4 built-in Selenium Manager
            driver = webdriver.Chrome(options=options)
        except Exception as e_builtin:
            # 2. Fall back to webdriver_manager if installed
            if HAS_WEBDRIVER_MANAGER:
                try:
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                except Exception:
                    raise e_builtin
            else:
                raise e_builtin

        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        wait = WebDriverWait(driver, timeout)

        # ── Open Google ────────────────────────────────────
        print(f"[STEP 2] Navigating to {TARGET_URL} ...", flush=True)
        driver.get(TARGET_URL)
        time.sleep(step_delay)
        print(f"[INFO]  Page title: {driver.title}", flush=True)

        # ── Dismiss consent popup if present ───────────────
        _dismiss_consent(driver, wait)
        time.sleep(1)

        # ── Locate search box ──────────────────────────────
        print(f"[STEP 3] Entering search query: '{search_query}' ...", flush=True)
        try:
            search_box = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea[name='q'], input[name='q']"))
            )
        except TimeoutException:
            search_box = wait.until(
                EC.presence_of_element_located((By.NAME, "q"))
            )

        search_box.clear()
        time.sleep(0.5)

        # Type query (character by character for visual feedback if not headless)
        if headless:
            search_box.send_keys(search_query)
        else:
            for char in search_query:
                search_box.send_keys(char)
                time.sleep(0.06)

        time.sleep(step_delay)
        search_box.send_keys(Keys.RETURN)

        # ── Wait for results ───────────────────────────────
        print("[STEP 4] Waiting for search results...", flush=True)
        found = _wait_for_results(driver, wait)
        if not found:
            print("[WARN]  Known selectors timed out; waiting for DOM to settle...", flush=True)
            time.sleep(3)

        time.sleep(step_delay)
        print(f"[INFO]  Results page title: {driver.title}", flush=True)

        # ── Collect top result headings ────────────────────
        print("[STEP 5] Collecting top search results...", flush=True)
        results = driver.find_elements(By.CSS_SELECTOR, "h3")
        visible = [r for r in results if r.is_displayed() and r.text.strip()]
        print(f"[INFO]  Found {len(visible)} visible result headings", flush=True)

        if not visible:
            print("[WARN]  No result headings found. Page source snippet:", flush=True)
            print(driver.page_source[:500], flush=True)
        else:
            for i, r in enumerate(visible[:5], 1):
                print(f"  [{i}] {r.text.strip()}", flush=True)

        time.sleep(step_delay)
        print("-" * 50, flush=True)
        print("[SUCCESS] Selenium script completed successfully!", flush=True)
        if not headless:
            time.sleep(1)

    except Exception as e:
        print(f"[ERROR] Script failed: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    finally:
        if driver is not None:
            try:
                driver.quit()
                print("[INFO] Browser closed.", flush=True)
            except Exception as e_close:
                print(f"[WARN] Error closing browser: {e_close}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Selenium Google Search Demo")
    parser.add_argument("--query", "-q", type=str, default=DEFAULT_SEARCH_QUERY, help="Search query")
    parser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode")
    parser.add_argument("--delay", type=float, default=DEFAULT_STEP_DELAY, help="Delay between steps in seconds")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Wait timeout in seconds")

    args, unknown = parser.parse_known_args()

    run(
        search_query=args.query,
        headless=args.headless,
        step_delay=args.delay,
        timeout=args.timeout,
    )
