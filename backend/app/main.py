import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import numpy as np

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .database import get_db, check_is_mock
from .dummy_data import generate_dummy_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically generate dummy data on startup
    print("Initializing Database with Dummy Data...")
    generate_dummy_data()
    yield

app = FastAPI(
    title="AI Tools Insights Dashboard API",
    description="Backend API to fetch MongoDB analytics and metrics",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "AI Tools Analytics API is running.",
        "dashboard_url": "http://localhost:5173",
        "interactive_api_docs": "http://127.0.0.1:8000/docs"
    }

@app.get("/api/status")
def get_status():
    return {
        "status": "online",
        "database": "mock_in_memory" if check_is_mock() else "real_mongodb",
        "time": datetime.now().isoformat()
    }

@app.get("/api/tools")
def get_tools():
    return [
        {"key": "gpt_tool", "label": "GPT Tool"},
        {"key": "text_to_image", "label": "Text-to-Image"},
        {"key": "translation", "label": "Translation"},
        {"key": "pdf_chat", "label": "PDF Chat"},
        {"key": "mom_transcription", "label": "MoM Transcription"},
        {"key": "overall", "label": "Overall Platform"}
    ]

@app.get("/api/insights/{tool_key}")
def get_insights(tool_key: str):
    db_file = get_db("file_DB")
    db_auth = get_db("auth_DB")
    db_user = get_db("user_DB")
    db_ai = get_db("ai_tools")
    db_pdf_chat = get_db("chat_with_pdf_qdrant")
    db_mom = get_db("mom")

    # Fetch data lists to aggregate in Python for 100% mongomock safety
    users = list(db_auth["User"].find())
    pdf_tracks = list(db_file["PdfTrack"].find())
    chat_responses = list(db_user["ChatResponse"].find())
    sessions = list(db_ai["sessions"].find())
    conversations = list(db_ai["conversations"].find())
    tasks = list(db_ai["processing_tasks"].find())

    # Map profile/module lists
    gpt_modules = ["Legal Draft GPT", "Contract Analyzer GPT", "Refactoring Assistant", "Market Trends GPT"]
    gpt_profiles = ["Legal Advisor", "Code Companion", "Finance Analyst"]

    if tool_key == "gpt_tool":
        # Filter PDF tracks and chats for GPT
        gpt_tracks = [t for t in pdf_tracks if t.get("module") in gpt_modules]
        gpt_chats = chat_responses # In our dummy generator, ChatResponses are for GPT
        
        # 1. Total uploads (GPT tracks)
        total_uploads = len(gpt_tracks)
        
        # 2. Ingestion completion rate
        completed_tracks = [t for t in gpt_tracks if t.get("training_done") is True]
        completion_rate = (len(completed_tracks) / total_uploads * 100) if total_uploads > 0 else 0
        
        # 3. Sessions & Message counts
        active_sessions = len(sessions)
        avg_messages = np.mean([s.get("message_count", 0) for s in sessions]) if sessions else 0
        
        # 4. Feedback & Response times
        feedbacks = []
        start_token_times = []
        last_token_times = []
        chat_date_entries = {} # for silent failures and timeseries
        
        for chat in gpt_chats:
            for entry in chat.get("chat_entries", []):
                fb = entry.get("feedback", "neutral")
                st = entry.get("start_token_time", 300)
                lt = entry.get("last_token_time", 2500)
                feedbacks.append(fb)
                start_token_times.append(st)
                last_token_times.append(lt)
                
                # date extraction
                dt_list = entry.get("date", [])
                if dt_list:
                    dt = dt_list[0]
                    if isinstance(dt, str):
                        dt = datetime.fromisoformat(dt.replace("Z", ""))
                    date_str = dt.strftime("%Y-%m-%d")
                    chat_date_entries.setdefault(date_str, []).append((fb, st, lt))

        # Thumbs counts
        fb_counts = {
            "thumbs_up": feedbacks.count("thumbs_up"),
            "thumbs_down": feedbacks.count("thumbs_down"),
            "neutral": feedbacks.count("neutral")
        }
        total_fb = len(feedbacks)
        pct_positive = (fb_counts["thumbs_up"] / total_fb * 100) if total_fb > 0 else 0
        
        # Response time stats (TTFT and Total Latency)
        avg_start_token_time = np.mean(start_token_times) if start_token_times else 0
        avg_last_token_time = np.mean(last_token_times) if last_token_times else 0
        p90_last_token_time = np.percentile(last_token_times, 90) if last_token_times else 3000
        
        # Task success rate
        completed_tasks = [t for t in tasks if t.get("status") == "completed"]
        task_success_rate = (len(completed_tasks) / len(tasks) * 100) if tasks else 0
        
        # Calculate GPT Health Score (0-100)
        # Formula: (% positive feedback * 0.5) + (task success rate * 0.3) + (1 - normalized avg response time) * 20
        # normalized avg response time: capped at 5000ms, using total response latency (last_token_time)
        norm_rt_score = max(0, 1 - (avg_last_token_time / 5000))
        health_score = (pct_positive * 0.5) + (task_success_rate * 0.3) + (norm_rt_score * 20)
        
        # --- Charts ---
        # A. Daily uploads (last 30 days)
        daily_uploads_dict = {}
        for track in gpt_tracks:
            ut = track.get("upload_time")
            if isinstance(ut, str):
                ut = datetime.fromisoformat(ut.replace("Z", ""))
            if ut:
                date_str = ut.strftime("%Y-%m-%d")
                daily_uploads_dict[date_str] = daily_uploads_dict.get(date_str, 0) + 1
        
        # Sort and construct 30 day range
        today = datetime.now()
        daily_uploads_chart = []
        for i in range(30):
            d = (today - timedelta(days=29 - i)).strftime("%Y-%m-%d")
            daily_uploads_chart.append({
                "date": d,
                "uploads": daily_uploads_dict.get(d, 0)
            })

        # B. Most-used profiles
        profile_counts = {}
        for track in gpt_tracks:
            prof = track.get("profile", "Unknown")
            profile_counts[prof] = profile_counts.get(prof, 0) + 1
        most_used_profiles_chart = [
            {"profile": k, "count": v} for k, v in sorted(profile_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        # C. Message volume by role per day
        # In our sessions data: conversations have roles "user" vs "assistant"
        msg_volume_dict = {}
        for conv in conversations:
            ts = conv.get("timestamp")
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace("Z", ""))
            if ts:
                d_str = ts.strftime("%Y-%m-%d")
                role = conv.get("role", "user")
                msg_volume_dict.setdefault(d_str, {"user": 0, "assistant": 0})
                msg_volume_dict[d_str][role] += 1
        
        message_volume_chart = []
        for i in range(30):
            d = (today - timedelta(days=29 - i)).strftime("%Y-%m-%d")
            entry = msg_volume_dict.get(d, {"user": 0, "assistant": 0})
            message_volume_chart.append({
                "date": d,
                "user": entry["user"],
                "assistant": entry["assistant"]
            })

        # D. Response time distribution (Buckets)
        # Buckets: <500ms, 500ms-1s, 1s-2s, 2s-3s, 3s-5s, >5s
        buckets = {
            "< 500ms": 0,
            "500ms - 1s": 0,
            "1s - 2s": 0,
            "2s - 3s": 0,
            "3s - 5s": 0,
            "> 5s": 0
        }
        for rt in last_token_times:
            if rt < 500:
                buckets["< 500ms"] += 1
            elif rt < 1000:
                buckets["500ms - 1s"] += 1
            elif rt < 2000:
                buckets["1s - 2s"] += 1
            elif rt < 3000:
                buckets["2s - 3s"] += 1
            elif rt < 5000:
                buckets["3s - 5s"] += 1
            else:
                buckets["> 5s"] += 1
        
        response_time_chart = [{"bucket": k, "count": v} for k, v in buckets.items()]

        # E. Silent Failure Rate (slow neutral feedback responses / total per day)
        silent_failures_chart = []
        latency_trend_chart = []
        for i in range(30):
            d = (today - timedelta(days=29 - i)).strftime("%Y-%m-%d")
            entries = chat_date_entries.get(d, [])
            if not entries:
                silent_failures_chart.append({"date": d, "rate": 0})
                latency_trend_chart.append({
                    "date": d,
                    "avg_ttft": 0,
                    "avg_total_time": 0
                })
                continue
            
            silent_count = sum(1 for fb, st, lt in entries if fb == "neutral" and lt > p90_last_token_time)
            rate = (silent_count / len(entries) * 100)
            silent_failures_chart.append({
                "date": d,
                "rate": round(rate, 2)
            })
            
            avg_ttft = np.mean([st for fb, st, lt in entries])
            avg_total = np.mean([lt for fb, st, lt in entries])
            latency_trend_chart.append({
                "date": d,
                "avg_ttft": round(avg_ttft, 0),
                "avg_total_time": round(avg_total, 0)
            })

        return {
            "metrics": {
                "active_sessions": active_sessions,
                "total_uploads": total_uploads,
                "avg_messages_per_session": round(avg_messages, 1),
                "completion_rate": round(completion_rate, 1),
                "health_score": round(health_score, 1),
                "avg_start_token_time_ms": round(avg_start_token_time, 0),
                "avg_last_token_time_ms": round(avg_last_token_time, 0),
                "avg_response_time_ms": round(avg_last_token_time, 0),
                "pct_positive_feedback": round(pct_positive, 1)
            },
            "charts": {
                "daily_uploads": daily_uploads_chart,
                "most_used_profiles": most_used_profiles_chart,
                "message_volume": message_volume_chart,
                "feedback_distribution": [
                    {"name": "Thumbs Up", "value": fb_counts["thumbs_up"]},
                    {"name": "Thumbs Down", "value": fb_counts["thumbs_down"]},
                    {"name": "Neutral", "value": fb_counts["neutral"]}
                ],
                "response_time_distribution": response_time_chart,
                "silent_failures": silent_failures_chart,
                "latency_trend": latency_trend_chart
            }
        }

    elif tool_key == "text_to_image":
        # Text to image analytics
        t2i_usage = list(db_ai["text_to_image_usage"].find())
        total_gen = sum(u.get("generated_count", 0) for u in t2i_usage)
        daily_limit = 50 # Config default
        unique_users = len(set(u.get("user_id") for u in t2i_usage))
        
        # Usage vs Quota (aggregated by date)
        usage_by_date = {}
        for u in t2i_usage:
            d = u.get("created_on")
            if d:
                usage_by_date[d] = usage_by_date.get(d, 0) + u.get("generated_count", 0)
        
        today = datetime.now()
        usage_quota_chart = []
        for i in range(10):
            d = (today - timedelta(days=9 - i)).strftime("%Y-%m-%d")
            val = usage_by_date.get(d, 0)
            usage_quota_chart.append({
                "date": d,
                "generated": val,
                "quota": daily_limit
            })

        # Feature A: Settings Trend (Inference steps vs Guidance scale over 10 days)
        t2i_hist = list(db_ai["text_to_image_history"].find())
        steps_guidance_by_date = {}
        for h in t2i_hist:
            d = h.get("created_on")
            if d:
                steps_guidance_by_date.setdefault(d, []).append((h.get("inference_steps", 30), h.get("guidance_scale", 7.5)))
        
        settings_trend_chart = []
        for i in range(10):
            d = (today - timedelta(days=9 - i)).strftime("%Y-%m-%d")
            entries = steps_guidance_by_date.get(d, [])
            if not entries:
                settings_trend_chart.append({
                    "date": d,
                    "avg_steps": 30.0,
                    "avg_guidance": 7.5
                })
            else:
                avg_steps = np.mean([s for s, g in entries])
                avg_guidance = np.mean([g for s, g in entries])
                settings_trend_chart.append({
                    "date": d,
                    "avg_steps": round(float(avg_steps), 1),
                    "avg_guidance": round(float(avg_guidance), 1)
                })

        # Feature B: Resolution Distribution
        res_counts = {}
        for h in t2i_hist:
            res = f"{h.get('width', 512)}x{h.get('height', 512)}"
            res_counts[res] = res_counts.get(res, 0) + 1
        resolution_chart = [{"name": k, "value": v} for k, v in res_counts.items()]
            
        return {
            "metrics": {
                "total_generated": total_gen,
                "daily_limit": daily_limit,
                "active_users": unique_users
            },
            "charts": {
                "usage_vs_quota": usage_quota_chart,
                "settings_trend": settings_trend_chart,
                "resolution_distribution": resolution_chart
            }
        }

    elif tool_key == "translation":
        trans_history = list(db_ai["translation_history"].find())
        total_translations = len(trans_history)
        
        # Group translation languages
        lang_counts = {}
        for t in trans_history:
            pair = f"{t.get('source_language', 'unknown')} -> {t.get('target_language', 'unknown')}"
            lang_counts[pair] = lang_counts.get(pair, 0) + 1
            
        language_pairs_chart = [
            {"pair": k, "count": v} for k, v in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        ]

        # Feature A: Daily translation volume over 15 days
        today = datetime.now()
        trans_by_date = {}
        for t in trans_history:
            ts = t.get("timestamp")
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace("Z", ""))
            if ts:
                d_str = ts.strftime("%Y-%m-%d")
                trans_by_date[d_str] = trans_by_date.get(d_str, 0) + 1
        
        daily_trend_chart = []
        for i in range(15):
            d = (today - timedelta(days=14 - i)).strftime("%Y-%m-%d")
            daily_trend_chart.append({
                "date": d,
                "count": trans_by_date.get(d, 0)
            })

        # Feature B: Translation Mode Breakdown (Text Translation vs. Voice Translation)
        feat_counts = {}
        for t in trans_history:
            feat = t.get("feature", "text_translation").replace("_", " ").title()
            feat_counts[feat] = feat_counts.get(feat, 0) + 1
        feature_chart = [{"name": k, "value": v} for k, v in feat_counts.items()]
        
        return {
            "metrics": {
                "total_translations": total_translations,
                "languages_supported": 8,
                "voice_translations": feat_counts.get("Voice Translation", 0)
            },
            "charts": {
                "language_pairs": language_pairs_chart,
                "daily_translation_trend": daily_trend_chart,
                "feature_breakdown": feature_chart
            }
        }

    elif tool_key == "pdf_chat":
        builds = list(db_pdf_chat["build_status"].find())
        success = [b for b in builds if b.get("status") == "success"]
        failed = [b for b in builds if b.get("status") == "failed"]
        success_rate = (len(success) / len(builds) * 100) if builds else 0
        
        avg_speed = np.mean([b.get("pages_processed", 0) / max(1, b.get("total_pages", 1)) for b in builds]) * 100 if builds else 0

        # Daily build counts
        builds_by_date = {}
        pages_by_date = {}
        for b in builds:
            dt = b.get("updated_at")
            if isinstance(dt, str):
                dt = datetime.fromisoformat(dt.replace("Z", ""))
            if dt:
                d_str = dt.strftime("%Y-%m-%d")
                builds_by_date.setdefault(d_str, {"success": 0, "failed": 0})
                if b.get("status") == "success":
                    builds_by_date[d_str]["success"] += 1
                else:
                    builds_by_date[d_str]["failed"] += 1
                pages_by_date[d_str] = pages_by_date.get(d_str, 0) + b.get("pages_processed", 0)
        
        today = datetime.now()
        build_history_chart = []
        pages_processed_chart = []
        for i in range(15):
            d = (today - timedelta(days=14 - i)).strftime("%Y-%m-%d")
            entry = builds_by_date.get(d, {"success": 0, "failed": 0})
            build_history_chart.append({
                "date": d,
                "success": entry["success"],
                "failed": entry["failed"]
            })
            pages_processed_chart.append({
                "date": d,
                "pages": pages_by_date.get(d, 0)
            })

        # Feature A: Document Type Breakdown
        docs = list(db_ai["documents"].find())
        doc_types = {}
        for d in docs:
            dtype = d.get("document_type", "Other").replace("_", " ").title()
            doc_types[dtype] = doc_types.get(dtype, 0) + 1
        doc_type_chart = [{"name": k, "value": v} for k, v in doc_types.items()]

        # Feature B: Uploaded File Types
        uploaded = list(db_ai["uploaded_files"].find())
        file_types = {}
        for f in uploaded:
            ftype = f.get("file_type", "pdf").upper()
            file_types[ftype] = file_types.get(ftype, 0) + 1
        file_type_chart = [{"name": k, "value": v} for k, v in file_types.items()]

        return {
            "metrics": {
                "build_success_rate": round(success_rate, 1),
                "total_builds": len(builds),
                "avg_ingestion_completion": f"{round(avg_speed, 1)}%"
            },
            "charts": {
                "build_status_split": [
                    {"name": "Success", "value": len(success)},
                    {"name": "Failed", "value": len(failed)}
                ],
                "build_history": build_history_chart,
                "daily_pages_processed": pages_processed_chart,
                "document_type_breakdown": doc_type_chart,
                "file_type_breakdown": file_type_chart
            }
        }

    elif tool_key == "mom_transcription":
        records = list(db_mom["records"].find())
        total_meetings = len(records)
        completed = [r for r in records if r.get("mom_status") == "completed"]
        
        # Funnel stage completion
        trans_done = len([r for r in records if r.get("transcription_status") == "completed"])
        summary_done = len([r for r in records if r.get("summary_status") == "completed"])
        mom_done = len(completed)
        
        funnel_chart = [
            {"stage": "1. Transcription", "count": trans_done},
            {"stage": "2. Summary", "count": summary_done},
            {"stage": "3. MoM Export", "count": mom_done}
        ]

        # Feature A: Daily meeting audio trend
        today = datetime.now()
        meetings_by_date = {}
        for r in records:
            dt = r.get("created_at")
            if isinstance(dt, str):
                dt = datetime.fromisoformat(dt.replace("Z", ""))
            if dt:
                d_str = dt.strftime("%Y-%m-%d")
                meetings_by_date[d_str] = meetings_by_date.get(d_str, 0) + 1
        
        meetings_trend_chart = []
        for i in range(15):
            d = (today - timedelta(days=14 - i)).strftime("%Y-%m-%d")
            meetings_trend_chart.append({
                "date": d,
                "count": meetings_by_date.get(d, 0)
            })

        # Feature B: Speaker Breakdown
        speaker_counts = {}
        for r in records:
            sp = f"{r.get('unique_speakers', 2)} Speakers"
            speaker_counts[sp] = speaker_counts.get(sp, 0) + 1
        speaker_chart = [{"name": k, "value": v} for k, v in speaker_counts.items()]
        
        return {
            "metrics": {
                "total_meetings": total_meetings,
                "completed_moms": mom_done,
                "pending_moms": total_meetings - mom_done
            },
            "charts": {
                "pipeline_funnel": funnel_chart,
                "daily_meeting_trend": meetings_trend_chart,
                "speaker_breakdown": speaker_chart
            }
        }

    elif tool_key == "overall":
        # Active vs Dormant
        cutoff = datetime.now() - timedelta(days=7)
        active_users = sum(1 for u in users if u.get("last_login_at") and (datetime.fromisoformat(u["last_login_at"].replace("Z", "")) if isinstance(u["last_login_at"], str) else u["last_login_at"]) > cutoff)
        
        # Leaderboard of top visited users
        leaderboard = [
            {"username": u.get("fullname", "User"), "visits": u.get("visited", 0)}
            for u in sorted(users, key=lambda x: x.get("visited", 0), reverse=True)[:5]
        ]
        
        # Tool category counts based on PdfTracks
        module_counts = {}
        for track in pdf_tracks:
            mod = track.get("module", "Other")
            module_counts[mod] = module_counts.get(mod, 0) + 1
            
        category_usage_chart = [
            {"name": k, "value": v} for k, v in sorted(module_counts.items(), key=lambda x: x[1], reverse=True)[:6]
        ]

        # Feature A: Platform Health score leaderboard
        builds = list(db_pdf_chat["build_status"].find())
        pdf_success_rate = (len([b for b in builds if b.get("status") == "success"]) / max(1, len(builds))) * 100
        mom_records = list(db_mom["records"].find())
        mom_completed_rate = (len([r for r in mom_records if r.get("mom_status") == "completed"]) / max(1, len(mom_records))) * 100
        
        chat_entries = list(db_user["ChatResponse"].find())
        all_feedbacks = [e.get("feedback", "neutral") for c in chat_entries for e in c.get("chat_entries", [])]
        gpt_pos_rate = (all_feedbacks.count("thumbs_up") / max(1, len(all_feedbacks))) * 100
        gpt_health = (gpt_pos_rate * 0.5) + (85 * 0.3) + (0.92 * 20)
        
        health_leaderboard = [
            {"tool": "GPT Assistant", "score": round(gpt_health, 1)},
            {"tool": "PDF Chat Agent", "score": round(pdf_success_rate, 1)},
            {"tool": "Speech Translator", "score": 82.5},
            {"tool": "Text to Image", "score": 88.0},
            {"tool": "MoM Creator", "score": round(mom_completed_rate, 1)}
        ]
        health_leaderboard = sorted(health_leaderboard, key=lambda x: x["score"], reverse=True)

        # Feature B: Satisfaction vs Speed Scatter Data
        trans_history = list(db_ai["translation_history"].find())
        t2i_usage = list(db_ai["text_to_image_usage"].find())
        satisfaction_speed_data = [
            {"tool": "GPT Assistant", "latency": 2.2, "satisfaction": 74, "volume": len(chat_entries)},
            {"tool": "PDF Chat Agent", "latency": 4.5, "satisfaction": 88, "volume": len(builds)},
            {"tool": "Speech Translator", "latency": 1.2, "satisfaction": 80, "volume": len(trans_history)},
            {"tool": "Text to Image", "latency": 5.5, "satisfaction": 68, "volume": len(t2i_usage)},
            {"tool": "MoM Creator", "latency": 9.0, "satisfaction": 72, "volume": len(mom_records)}
        ]
        
        return {
            "metrics": {
                "total_users": len(users),
                "active_7d_users": active_users,
                "dormant_users": len(users) - active_users
            },
            "charts": {
                "power_users": leaderboard,
                "category_usage": category_usage_chart,
                "health_leaderboard": health_leaderboard,
                "satisfaction_speed": satisfaction_speed_data
            }
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid tool key specified")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
