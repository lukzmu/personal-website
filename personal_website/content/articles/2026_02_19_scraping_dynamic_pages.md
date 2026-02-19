Title: Scraping dynamic pages with Python, Playwright and AWS Lambda
Date: 2026-02-19 10:00

If you have ever pointed `BeautifulSoup` at a modern job board and then wondered why you got only a fraction of the visible listings, welcome to the club. Many of these pages behave like mini frontends: data appears in chunks, the DOM keeps changing, and scrolling is effectively part of the API contract. For this walkthrough, I used the [Dev IT Jobs](https://devitjobs.uk/) portal as a practical example.

This post breaks down a Lambda scraper that survives that behavior. The idea is simple but battle-tested: use Playwright + headless Chromium to trigger dynamic loading, extract records while scrolling, shape the result with Polars, and store snapshots as parquet in S3 partitions. It is serverless, schedule-friendly, and ready for downstream analytics without extra cleanup.

## Imports and runtime setup

Packages used in the Lambda:

- `playwright`: runs a Chromium browser so JavaScript-rendered cards can be collected,
- `boto3`: uploads the final parquet artifact to S3,
- `polars`: converts raw records into a dataframe and writes parquet efficiently,
- `pendulum`: provides cleaner timestamp handling for metadata and S3 partition keys,
- `aws_lambda_typing`: adds explicit types for the Lambda handler contract *(optional)*.

Standard-library helpers:

- `logging`: emits structured runtime logs for CloudWatch,
- `os`: reads environment configuration such as `BUCKET_URL`,
- `tempfile`: writes temporary files to Lambda's `/tmp` storage,
- `time`: adds short pauses so lazy-loaded DOM elements can render,
- `urllib.parse`: parses the bucket name from URL-like configuration values.

## Opening the page and targeting the scrollable list

The first step is launching Chromium in headless mode and identifying the actual element that reacts to scroll events. On this page, `.joblist-container` is where new cards are appended, so scrolling the whole page does not reliably pull in the full dataset.

```python
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-setuid-sandbox",
            "--no-sandbox",
            "--single-process",
        ],
    )
    page = browser.new_page()
    page.goto(url, wait_until="networkidle")

    container = page.locator(".joblist-container").first
```

Those Chromium flags are not "nice-to-have tuning", but rather we need to set them so that playwright works correctly in AWS Lambda:

- `--disable-gpu` avoids hardware acceleration paths that do not help here,
- `--disable-dev-shm-usage` steers Chromium away from shared-memory assumptions that can be too tight in serverless containers,
- `--disable-setuid-sandbox` and `--no-sandbox` help when sandbox initialization fails in restricted environments,
- `--single-process` also reduced startup flakiness. Without this set, the function was far more likely to fail before scraping anything useful.

## Scraping records while the page reveals more items

The extraction loop does one boring but powerful thing on repeat: wait a moment, read visible `li` cards, save what matters, scroll, and repeat. Dynamic pages frequently repaint old nodes, so `handled_jobs` is a must-have to avoid collecting duplicates when the same listing shows up again after a re-render.

```python
postings = []
found_last = False
handled_jobs = set()

while not found_last:
    time.sleep(0.5)  # Allow site to load new data after scroll
    li_items = container.locator("li")

    for i in range(li_items.count()):
        item = li_items.nth(i)

        # Sentinel block that appears at the end of the list
        title = item.locator(".jobteaser-name-header").first.text_content().strip()
        if title == "Haven't found your dream Data job yet?":
            found_last = True
            break

        # Gather any fields you care about.

        postings.append(...)
        handled_jobs.add(...)  # Usually the job URL or another stable identifier

    page.eval_on_selector(
        "div.joblist-container div div",
        "el => { el.scrollTop += 288 }",
    )
```

The sentinel title (`Haven't found your dream Data job yet?`) gives a deterministic exit and avoids guesswork like "scroll exactly N times and hope for the best."

## One extra guardrail worth adding

I also recommend a hard cap on scroll iterations. If the markup changes and the sentinel disappears, the function still exits cleanly instead of looping until timeout.

```python
max_scrolls = 300
scrolls = 0

while not found_last and scrolls < max_scrolls:
    ...
    page.eval_on_selector("div.joblist-container div div", "el => { el.scrollTop += 288 }")
    scrolls += 1

if scrolls == max_scrolls:
    logger.warning("Max scroll limit reached before sentinel. Site layout may have changed.")
```

## Writing parquet and uploading to S3

After scraping, the handler converts the payload into a Polars dataframe, normalizes column types as strings, writes parquet to `/tmp`, and uploads the file to a partitioned S3 key. This makes downstream ingestion easier, since each Lambda run produces a compact file in a predictable location.

```python
def lambda_handler(event: EventBridgeEvent, context: Context) -> dict[str, Any]:
    site_data = _parse_site(url="https://devitjobs.uk/jobs/Data/all")
    df = pl.DataFrame(site_data)
    df = df.select(pl.all().cast(pl.String))  # Casting to string for simplicity

    date = pendulum.now()
    file_name = f"{date.timestamp()}.parquet"
    file_path = f"{tempfile.gettempdir()}/{file_name}"
    df.write_parquet(file_path)

    bucket_name = urlparse(_BUCKET_URL).netloc
    client = boto3.client(service_name="s3")

    # Each directory creates a partition when you use Glue Crawler. 
    # You can go even deeper, if you want.
    key = f"dev_it_jobs/postings/year={date.year}/month={date.month}/{file_name}"

    client.upload_file(Filename=file_path, Bucket=bucket_name, Key=key)

    return {"statusCode": 200, "message": "Dev IT Jobs handled correctly"}
```

Parquet keeps storage efficient and query-friendly, and the date partitioning keeps recurring snapshots tidy for Athena, Spark, or any ETL flow you throw at it.

## Practical notes for dynamic pages in Lambda

If I had to compress this whole post into one sentence, it would be this: dynamic scraping in Lambda is mostly about controlling browser behavior, not parsing HTML faster. Once the browser is stable, the rest becomes a clean data-engineering loop.

What to take out of this post is a practical blueprint you can reuse on similar pages. First, identify the actual scrollable container that triggers lazy loading. Second, keep the extraction loop stateful and deterministic (`handled_jobs`, `found_last`, and ideally a max-scroll guardrail). Third, write the output in an analytics-friendly format (parquet) and store it in partitioned S3 paths so downstream jobs can read incrementally. It is a simple pattern, but it scales surprisingly well for scheduled ingestion and is easy to debug when the target site changes.
