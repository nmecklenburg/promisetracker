from openai import AzureOpenAI


def extract_promises(urls: list[str]) -> list[dict]:
    return [
        {
            "_timestamp": "2024-01-05",
            "status": 0,
            "text": "some sample text",
            "citations": [
                {
                    "date": "2024-08-01",
                    "extract": "this is a sample extract",
                    "url": "https://www.google.com"
                },
                {
                    "date": "2008-05-13",
                    "extract": "this is a second sample extract",
                    "url": "https://www.bing.com"
                }
            ],
        },
        {
            "_timestamp": "2024-01-07",
            "status": 2,
            "text": "some more sample text",
            "citations": [
                {
                    "date": "2024-07-12",
                    "extract": "this is a third sample extract",
                    "url": "https://www.stanford.edu"
                },
                {
                    "date": "2011-12-21",
                    "extract": "this is a fourth sample extract",
                    "url": "https://www.berkeley.edu"
                }
            ],
        },
    ]
