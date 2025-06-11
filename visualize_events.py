import json
import argparse
from datetime import datetime, timedelta


def parse_time(t: str) -> int:
    minutes, seconds = map(int, t.split(":"))
    return minutes * 60 + seconds


COLORS = {
    "motion": "#ffcc00",
    "quick_motion": "#ff6600",
    "person": "#0099ff",
}


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"UTF-8\" />
<title>Event Timeline</title>
<style>
body {{ font-family: Arial, sans-serif; padding: 20px; }}
.timeline {{ position: relative; height: 40px; background: #eee; }}
.segment {{ position: absolute; height: 100%; }}
.label {{ position: absolute; top: 45px; font-size: 12px; }}
</style>
</head>
<body>
<div class=\"timeline\">
{segments}
</div>
{labels}
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Visualize events JSON")
    parser.add_argument("json_file")
    parser.add_argument("--output", default="timeline.html")
    args = parser.parse_args()

    with open(args.json_file, encoding="utf-8") as fh:
        data = json.load(fh)

    events = data.get("events", [])
    if not events:
        print("No events found")
        return

    end_time = max(parse_time(ev["end"]) for ev in events)
    segments_html = []
    labels_html = []
    for ev in events:
        start = parse_time(ev["start"]) * 100 / end_time
        end = parse_time(ev["end"]) * 100 / end_time
        width = end - start
        color = COLORS.get(ev["type"], "#666")
        segments_html.append(
            f'<div class="segment" style="left:{start}%;width:{width}%;background:{color}"></div>'
        )
        labels_html.append(
            f'<div class="label" style="left:{start}%">{ev["type"]}</div>'
        )

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(
            HTML_TEMPLATE.format(
                segments="\n".join(segments_html), labels="\n".join(labels_html)
            )
        )
    print(f"Timeline saved to {args.output}")


if __name__ == "__main__":
    main()
