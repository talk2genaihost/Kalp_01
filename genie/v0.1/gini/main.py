from .schemas import CreativeRequest
from .pipeline import write_slice
import argparse, json

def main():
    ap = argparse.ArgumentParser(description="KALP Gini v0.1 executable planning slice")
    ap.add_argument("--idea", required=True)
    ap.add_argument("--output", default="gini_output")
    ap.add_argument("--platform", default="Instagram Reels")
    ap.add_argument("--language", default="Hindi")
    ap.add_argument("--duration", type=int, default=60)
    ap.add_argument("--aspect-ratio", default="9:16")
    args = ap.parse_args()
    req = CreativeRequest(
        request_id="REQ_CLI_001",
        user_intent=args.idea,
        content_type="short-form-reel",
        target_platform=args.platform,
        language=args.language,
        duration=args.duration,
        aspect_ratio=args.aspect_ratio,
        desired_outputs=["creative_plan", "18_scene_manifest"]
    )
    print(json.dumps(write_slice(args.output, req), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
