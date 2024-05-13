from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=50)
    page = browser.new_page()
    page.goto('https://dribbble.com/session/new')
    print(page.context.cookies())
    print()
    page.fill('input[name="login"]', 'logodiffusion2')
    page.fill('input[name="password"]', 'logodiffusion')
    page.click('input[type="submit"]')

    print(page.context.cookies())
    print()

    page.goto('https://dribbble.com/ZMasterDesigns')
    print(page.context.cookies())