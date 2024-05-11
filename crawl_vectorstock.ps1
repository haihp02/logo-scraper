$maxPage = 10
$designer = "hr_line"
$outputFile = "test_vectorstock_hr_line.jsonl"

for($i = 1; $i -le $maxPage; $i++) {
    scrapy crawl vectorstock_spider -a designer=$designer -a page_num=$i -o $outputFile
}