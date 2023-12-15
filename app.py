import flask
from flask import request
import asyncio
from typing import Optional
from playwright.async_api import async_playwright

app = flask.Flask(__name__)


async def generate_pdf(
        target_url: str,
        auth_token: Optional[str],
        destination_file: str,
        page_width: int = 1920,
        margin: int = 80
) -> None:

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(device_scale_factor=4)  # You can change the scale_factor to +/- images quality
        page.set_default_navigation_timeout(120000.0)
        await page.set_viewport_size({'width': page_width, 'height': 1080})
        await page.set_extra_http_headers(
            {'Authorization': f'Bearer {auth_token}'}
        )
        await page.goto(target_url)
        await page.wait_for_selector('.react-grid-layout')
        page_height = await page.evaluate(
            'document.getElementsByClassName(\'react-grid-layout\')[0].getBoundingClientRect().bottom;'
        )
        await page.set_viewport_size({'width': page_width, 'height': page_height})
        await page.wait_for_load_state('networkidle')
        await page.pdf(
            path=destination_file,
            scale=1,
            width=f'{page_width + margin * 2}px',
            height=f'{page_height + margin * 2}px',
            display_header_footer=False,
            print_background=True,
            margin={
                'top': f'{margin}px',
                'bottom': f'{margin}px',
                'left': f'{margin}px',
                'right': f'{margin}px',
            }
        )
        await browser.close()


async def main(grafana_auth_token, target_url):

    # target_url = os.environ.get('GRAFANA_URL_DASH')  # Tip: add '&kiosk' at the end of your grafana URL to hide tool tabs
    # grafana_auth_token: str = os.environ.get('GRAFANA_AUTH_TOKEN')
    destination_file: str = f'./grafana_report.pdf'

    await generate_pdf(
        target_url, grafana_auth_token, destination_file
    )




@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    body = request.get_json()
    grafana_auth_token = body.get('grafana_auth_token')
    target_url = body.get('target_url')

    if not grafana_auth_token:
        return flask.render_template('index.html', error='Grafana auth token is required')
    if not target_url:
        return flask.render_template('index.html', error='Grafana target url is required')
    
    asyncio.run(main(grafana_auth_token=grafana_auth_token, target_url=target_url))
    return flask.send_file('./grafana_report.pdf', as_attachment=True)
