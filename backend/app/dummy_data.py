import random
from datetime import datetime, timedelta
from bson import ObjectId
from .database import get_db

# Helper to generate random timestamps over the last 30 days
def random_date(start_days_ago=30, end_days_ago=0):
    start = datetime.now() - timedelta(days=start_days_ago)
    end = datetime.now() - timedelta(days=end_days_ago)
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    if int_delta <= 0:
        return datetime.now()
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)

def generate_dummy_data(force=False):
    # Fetch all database collection handlers
    db_services = get_db("ai_services")
    db_ai = get_db("ai_tools")
    db_auth = get_db("auth_DB")
    db_pdf_chat = get_db("chat_with_pdf_qdrant")
    db_file = get_db("file_DB")
    db_mom = get_db("mom")
    db_offline = get_db("offline_chatbot")
    db_sandarbh = get_db("sandarbh")
    db_scan = get_db("scan_to_word")
    db_scanned = get_db("scanned_to_readable")
    db_summ = get_db("summarization")
    db_user = get_db("user_DB")

    # Only populate if User collection is empty and force=False
    if not force and db_auth["User"].count_documents({}) > 0:
        print("Database already contains data. Skipping generation.")
        return

    # Clear everything across all databases
    for db in [db_services, db_ai, db_auth, db_pdf_chat, db_file, db_mom, db_offline, db_sandarbh, db_scan, db_scanned, db_summ, db_user]:
        for coll in db.list_collection_names():
            # Skip system collections
            if not coll.startswith("system."):
                db[coll].delete_many({})

    # 1. file_DB - Profiles, Modules, ManagedTool, offline_gpt_tools, SystemSettings
    profiles = [
        {"_id": ObjectId(), "name": "Legal Advisor", "isGPT": True, "gpt_managed": True, "description": "Legal drafting and contract review", "category": "Legal", "updated_at": datetime.now()},
        {"_id": ObjectId(), "name": "Code Companion", "isGPT": True, "gpt_managed": True, "description": "Coding support and review", "category": "Tech", "updated_at": datetime.now()},
        {"_id": ObjectId(), "name": "Finance Analyst", "isGPT": True, "gpt_managed": True, "description": "Financial reports interpretation", "category": "Finance", "updated_at": datetime.now()},
        {"_id": ObjectId(), "name": "HR Assistant", "isGPT": True, "gpt_managed": False, "description": "Offline policy search tool", "category": "HR", "updated_at": datetime.now()},
        {"_id": ObjectId(), "name": "Document Translator", "isGPT": False, "gpt_managed": False, "description": "Language Translation Profile", "category": "General", "updated_at": datetime.now()}
    ]
    db_file["Profiles"].insert_many(profiles)

    modules = [
        {"_id": ObjectId(), "name": "Legal Draft GPT", "profile_id": profiles[0]["_id"], "isGPT": True, "gpt_managed": True, "description": "Drafting legal documents", "category": "Legal", "updated_at": datetime.now()},
        {"_id": ObjectId(), "name": "Contract Analyzer GPT", "profile_id": profiles[0]["_id"], "isGPT": True, "gpt_managed": True, "description": "Analyzing contracts", "category": "Legal", "updated_at": datetime.now()},
        {"_id": ObjectId(), "name": "Refactoring Assistant", "profile_id": profiles[1]["_id"], "isGPT": True, "gpt_managed": True, "description": "Code refactoring advisor", "category": "Tech", "updated_at": datetime.now()},
        {"_id": ObjectId(), "name": "Market Trends GPT", "profile_id": profiles[2]["_id"], "isGPT": True, "gpt_managed": True, "description": "Market trend calculator", "category": "Finance", "updated_at": datetime.now()}
    ]
    db_file["Modules"].insert_many(modules)

    managed_tools = [
        {"_id": ObjectId(), "tool_key": "gpt_tool", "path": "/chat", "category_key": "chat", "category_label": "Conversational AI", "name": "GPT Tool", "description": "Interact with GPT models", "is_active": True, "sort_order": 1, "updated_at": datetime.now()},
        {"_id": ObjectId(), "tool_key": "translation", "path": "/translate", "category_key": "utility", "category_label": "Utilities", "name": "Translator", "description": "Translate documents and voice", "is_active": True, "sort_order": 2, "updated_at": datetime.now()},
        {"_id": ObjectId(), "tool_key": "text_to_image", "path": "/generate-image", "category_key": "media", "category_label": "Media Creation", "name": "Text to Image", "description": "Generate images from description", "is_active": True, "sort_order": 3, "updated_at": datetime.now()}
    ]
    db_file["ManagedTool"].insert_many(managed_tools)

    offline_gpt_tools = [
        {"_id": ObjectId(), "name": "Local Llama2", "path": "/models/llama2", "description": "Local offline chatbot", "prompt": "You are a helpful assistant", "inference_model": "Llama-2-7b-chat", "inference_url": "http://localhost:8080/v1", "is_active": True, "managed": True, "updated_at": datetime.now()}
    ]
    db_file["offline_gpt_tools"].insert_many(offline_gpt_tools)

    db_file["SystemSettings"].insert_one({
        "_id": ObjectId(),
        "key": "analytics_refresh_rate",
        "value": "300",
        "updated_at": datetime.now()
    })

    # 2. auth_DB - Role, User, AccessToken, RefreshToken, maintenance_mode
    roles = [
        {"_id": ObjectId(), "name": "Administrator", "permissions": ["all"]},
        {"_id": ObjectId(), "name": "User", "permissions": ["read", "write"]},
        {"_id": ObjectId(), "name": "Guest", "permissions": ["read"]}
    ]
    db_auth["Role"].insert_many(roles)

    users = []
    usernames = ["alice_dev", "bob_legal", "charlie_finance", "hr_admin", "guest_user"]
    emails = ["alice@company.com", "bob@company.com", "charlie@company.com", "hr@company.com", "guest@company.com"]
    for i, name in enumerate(usernames):
        users.append({
            "_id": ObjectId(),
            "email": emails[i],
            "fullname": name.replace("_", " ").title(),
            "hashed_password": "hashed_dummy_password_123",
            "is_active": True,
            "is_superuser": (name == "hr_admin"),
            "is_verified": True,
            "profiles_id": profiles[i]["_id"],
            "gpt_module_ids": [m["_id"] for m in modules],
            "offline_gpt_ids": [o["_id"] for o in offline_gpt_tools],
            "visited": random.randint(10, 150),
            "registered_at": random_date(45, 30),
            "last_login_at": random_date(5, 0),
            "user_category": "Internal",
            "organization": "AI Org",
            "designation": "Staff",
            "security_question": "Pet's name?",
            "security_answer": "hashed_answer",
            "role_id": roles[1]["_id"] if name != "hr_admin" else roles[0]["_id"],
            "block_reason": None
        })
    db_auth["User"].insert_many(users)

    access_tokens = []
    refresh_tokens = []
    for u in users:
        access_tokens.append({"_id": ObjectId(), "token": f"access_tok_{u['_id']}", "user_id": u["_id"], "created_at": datetime.now()})
        refresh_tokens.append({"_id": ObjectId(), "token": f"refresh_tok_{u['_id']}", "user_id": u["_id"], "created_at": datetime.now()})
    db_auth["AccessToken"].insert_many(access_tokens)
    db_auth["RefreshToken"].insert_many(refresh_tokens)

    db_auth["maintenance_mode"].insert_one({
        "_id": ObjectId(),
        "key": "system_maintenance",
        "enabled": False,
        "updated_at": datetime.now(),
        "updated_by": str(users[3]["_id"])
    })

    # 3. file_DB - PdfTrack
    pdf_tracks = []
    modules_list = ["Legal Draft GPT", "Contract Analyzer GPT", "Refactoring Assistant", "Market Trends GPT", "Offline Policy Finder", "Document Translator"]
    profiles_list = ["Legal Advisor", "Code Companion", "Finance Analyst", "HR Assistant", "Document Translator"]
    for _ in range(200):
        m_idx = random.randint(0, len(modules_list) - 1)
        p_idx = random.randint(0, len(profiles_list) - 1)
        u_idx = random.randint(0, len(users) - 1)
        up_time = random_date(30, 0)
        pdf_tracks.append({
            "_id": ObjectId(),
            "name": f"report_{random.randint(100,999)}.pdf",
            "username": users[u_idx]["fullname"],
            "profile": profiles_list[p_idx],
            "module": modules_list[m_idx],
            "pdfPath": f"/uploads/{usernames[u_idx]}/" + f"report_{random.randint(100,999)}.pdf",
            "training_done": random.random() < 0.88,
            "upload_time": up_time,
            "modification_time": up_time + timedelta(minutes=random.randint(1, 10)),
            "file_hash": f"hash_{random.randint(100000, 999999)}",
            "chunk_ids": [f"c_{i}" for i in range(random.randint(5, 20))]
        })
    db_file["PdfTrack"].insert_many(pdf_tracks)

    # 4. user_DB - ChatResponse (with start_token_time and last_token_time)
    chat_responses = []
    gpt_profiles = [p for p in profiles if p["isGPT"]]
    gpt_modules = modules
    questions = [
        "Explain this contract indemnification clause.",
        "Refactor this Python sorting algorithm to make it O(N log N).",
        "What was our Q2 net margin growth?",
        "Can you rewrite this section of the NDA?",
        "Write a unit test for this FastAPI endpoint.",
        "Summarize this auditor's statement.",
        "How do we handle intellectual property disputes?"
    ]
    answers = [
        "The indemnification clause specifies that Party A will cover damages and legal costs incurred by Party B...",
        "Sure, here is the optimized algorithm using Merge Sort which guarantees O(N log N) performance...",
        "Based on the upload statement, the Q2 net margin grew by 14.2% quarter-on-quarter, driven by cost savings...",
        "Here is the revised NDA clause: 'The Recipient shall keep all proprietary information strictly confidential...'",
        "Here is the Pytest code for the FastAPI route: `def test_read_root(): ...`",
        "The auditor concluded that the financial statements present fairly, in all material respects, the position of...",
        "Intellectual property is governed under Section 9, which reserves all trademark and patent rights to..."
    ]

    for _ in range(250):
        p = random.choice(gpt_profiles)
        m = random.choice([m for m in gpt_modules if m["profile_id"] == p["_id"]] or gpt_modules)
        u = random.choice(users)
        entries = []
        num_turns = random.randint(1, 4)
        for _ in range(num_turns):
            q_idx = random.randint(0, len(questions) - 1)
            
            # Incorporating TTFT (start_token_time) and Latency (last_token_time) in ms
            start_tok = random.randint(100, 800)
            last_tok = start_tok + random.randint(500, 4000)
            
            r_val = random.random()
            if r_val < 0.70:
                feedback = "thumbs_up"
            elif r_val < 0.80:
                feedback = "thumbs_down"
            else:
                feedback = "neutral"

            entries.append({
                "question": questions[q_idx],
                "q_hash": f"h_{random.randint(100000, 999999)}",
                "answer": answers[q_idx],
                "reference": [
                    {"file": "contract.pdf", "page": 1, "page_numbers": [1, 2]}
                ],
                "source": ["document_context"],
                "date": [random_date(30, 0)],
                "feedback": feedback,
                "start_token_time": start_tok,
                "last_token_time": last_tok
            })
            
        chat_responses.append({
            "_id": ObjectId(),
            "user_id": u["_id"],
            "profile_id": p["_id"],
            "module_id": m["_id"],
            "date": [random_date(30, 0)],
            "chat_entries": entries
        })
    db_user["ChatResponse"].insert_many(chat_responses)

    # 5. ai_tools - conversations, sessions, processing_tasks, text_to_image_usage, text_to_image_config, translation_history
    # document_states, documents, uploaded_files, text_to_image_history
    sessions = []
    conversations = []
    for _ in range(35):
        u = random.choice(users)
        sess_id = f"sess_{random.randint(1000,9999)}"
        created_at = random_date(30, 0)
        msg_count = random.randint(2, 10)
        sessions.append({
            "_id": ObjectId(),
            "user_id": str(u["_id"]),
            "session_id": sess_id,
            "created_at": created_at,
            "last_activity": created_at + timedelta(minutes=msg_count * 2),
            "message_count": msg_count,
            "document_count": random.randint(0, 3),
            "uploaded_files_count": random.randint(0, 2),
            "supported_document_types": ["pdf", "txt", "docx"]
        })
        for i in range(msg_count):
            timestamp = created_at + timedelta(minutes=i * 2)
            role = "user" if i % 2 == 0 else "assistant"
            content = "User query text" if role == "user" else "Assistant reply text"
            conversations.append({
                "_id": ObjectId(),
                "user_id": str(u["_id"]),
                "session_id": sess_id,
                "role": role,
                "content": content,
                "timestamp": timestamp,
                "message_id": f"msg_{random.randint(100000,999999)}"
            })
    db_ai["sessions"].insert_many(sessions)
    db_ai["conversations"].insert_many(conversations)

    tasks = []
    for _ in range(50):
        u = random.choice(users)
        status = random.choice(["completed", "completed", "completed", "failed", "running"])
        pct = 100 if status == "completed" else (random.randint(0, 95) if status == "running" else random.randint(10, 80))
        created = random_date(30, 0)
        tasks.append({
            "_id": ObjectId(),
            "task_id": f"t_{random.randint(10000, 99999)}",
            "user_id": str(u["_id"]),
            "session_id": f"sess_{random.randint(1000,9999)}",
            "status": status,
            "progress_percentage": pct,
            "current_step": "Finishing up" if status == "completed" else "Processing nodes",
            "total_steps": 10,
            "completed_steps": 10 if status == "completed" else random.randint(1, 9),
            "error_message": "Pipeline timeout" if status == "failed" else None,
            "result": {"url": "http://result.link"} if status == "completed" else None,
            "created_at": created,
            "updated_at": created + timedelta(minutes=random.randint(1, 15))
        })
    db_ai["processing_tasks"].insert_many(tasks)

    db_ai["text_to_image_config"].insert_one({
        "_id": ObjectId(),
        "key": "daily_limit",
        "daily_limit": 50,
        "updated_at": datetime.now()
    })

    t2i_usages = []
    for u in users:
        for offset in range(5):
            created_on = (datetime.now() - timedelta(days=offset)).strftime("%Y-%m-%d")
            t2i_usages.append({
                "_id": ObjectId(),
                "user_id": str(u["_id"]),
                "created_on": created_on,
                "created_at": datetime.now().isoformat(),
                "generated_count": random.randint(2, 28),
                "updated_at": datetime.now().isoformat()
            })
    db_ai["text_to_image_usage"].insert_many(t2i_usages)

    translation_hist = []
    langs = ["en", "es", "fr", "de", "zh", "ar", "ja", "it"]
    for _ in range(60):
        src = random.choice(langs)
        tgt = random.choice([l for l in langs if l != src])
        translation_hist.append({
            "_id": ObjectId(),
            "user_id": str(random.choice(users)["_id"]),
            "input_text": "text to translate",
            "processed_audio_path": "/audio/trans.wav",
            "target_language": tgt,
            "feature": "text_translation",
            "timestamp": random_date(30, 0),
            "text": "original text",
            "translated_text": "translated text",
            "source_language": src,
            "file_name": "speech.wav",
            "uploaded_audio_path": "/audio/src.wav",
            "language": src,
            "transcribed_text": "speech text",
            "translated_audio_path": "/audio/out.wav"
        })
    db_ai["translation_history"].insert_many(translation_hist)

    document_states = []
    for _ in range(15):
        document_states.append({
            "_id": ObjectId(),
            "session_id": f"sess_{random.randint(1000,9999)}",
            "document_type": "legal_agreement",
            "user_id": str(random.choice(users)["_id"]),
            "state": {
                "document_type": "legal_agreement",
                "fixed_template": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "security_classification": "Confidential",
                "file_reference": "ref_101",
                "date": "2026-07-10",
                "sender_tele": "123-456",
                "sender_address": "Address 1",
                "to_addressees": ["recipient@company.com"],
                "cc_addressees": ["cc@company.com"],
                "subject": "Agreement Subject",
                "background": {"paragraph": "Background text", "points": ["Point 1"]},
                "main_body": {"paragraph": "Main content paragraph", "points": ["Clause A"]},
                "recommendation": {"paragraph": "Rec text", "points": ["Action 1"]},
                "dynamic_content": [],
                "signatory_name": "Signer Name",
                "signatory_rank": "Director",
                "signatory_designation": "Manager",
                "signatory_appointment": "VP",
                "annexures": [],
                "enclosures": [],
                "crest_url": "http://crest.png",
                "sender": {"name_with_decorations": "Sender Name", "appointment": "Mgr", "tele": "123", "address": "Addr", "fax": "456", "email": "sender@email.com"},
                "recipient": {"name_with_decorations": "Recipient Name", "address_line1": "Addr1", "address_line2": "Addr2", "address_line3": "Addr3"},
                "title": "Document Title",
                "salutation": "Dear Sir",
                "closing": "Yours sincerely"
            },
            "updated_at": datetime.now()
        })
    db_ai["document_states"].insert_many(document_states)

    documents = []
    for _ in range(15):
        documents.append({
            "_id": ObjectId(),
            "document_id": f"doc_{random.randint(100,999)}",
            "user_id": str(random.choice(users)["_id"]),
            "session_id": f"sess_{random.randint(1000,9999)}",
            "html_content": "<div>Document HTML content</div>",
            "document_type": "brief_memo",
            "document_data": {"document_type": "brief_memo", "fixed_template": False, "created_at": datetime.now(), "updated_at": datetime.now()},
            "created_at": datetime.now()
        })
    db_ai["documents"].insert_many(documents)

    uploaded_files = []
    for _ in range(15):
        u = random.choice(users)
        uploaded_files.append({
            "_id": ObjectId(),
            "user_id": str(u["_id"]),
            "file_id": f"file_{random.randint(1000,9999)}",
            "session_id": f"sess_{random.randint(1000,9999)}",
            "original_filename": f"document_{random.randint(1,50)}.pdf",
            "file_type": "pdf",
            "file_size": random.randint(10000, 5000000),
            "extracted_text": "Extracted document text context...",
            "is_soc": False,
            "upload_timestamp": datetime.now()
        })
    db_ai["uploaded_files"].insert_many(uploaded_files)

    t2i_history = []
    for _ in range(15):
        u = random.choice(users)
        t2i_history.append({
            "_id": ObjectId(),
            "user_id": str(u["_id"]),
            "image_id": f"img_{random.randint(1000,9999)}",
            "created_at": datetime.now().isoformat(),
            "created_on": datetime.now().strftime("%Y-%m-%d"),
            "enhanced_prompt": "Beautiful scenery prompt, high definition",
            "filename": f"image_{random.randint(100,999)}.png",
            "guidance_scale": 7.5,
            "height": 512,
            "image_api_path": "/api/images/img1.png",
            "image_path": "/images/img1.png",
            "inference_steps": 30,
            "prompt": "Scenery prompt",
            "record_id": f"rec_{random.randint(1000,9999)}",
            "width": 512
        })
    db_ai["text_to_image_history"].insert_many(t2i_history)

    # 6. chat_with_pdf_qdrant - build_status, history_messages, history_summaries, config, history
    builds = []
    for _ in range(20):
        u = random.choice(users)
        status = random.choice(["success", "success", "success", "failed"])
        tot_pages = random.choice([5, 15, 30, 60])
        pages_processed = tot_pages if status == "success" else random.randint(1, tot_pages - 1)
        builds.append({
            "_id": ObjectId(),
            "session_id": f"pdf_sess_{random.randint(100,999)}",
            "user_id": str(u["_id"]),
            "error": "Timeout occurred" if status == "failed" else "",
            "pages_processed": pages_processed,
            "total_pages": tot_pages,
            "status": status,
            "updated_at": random_date(30, 0)
        })
    db_pdf_chat["build_status"].insert_many(builds)

    history_messages = []
    for _ in range(10):
        history_messages.append({
            "_id": ObjectId(),
            "user_id": str(random.choice(users)["_id"]),
            "session_id": f"pdf_sess_{random.randint(100,999)}",
            "sequence": random.randint(1, 5),
            "role": random.choice(["user", "assistant"]),
            "content": "Message content",
            "created_at": datetime.now(),
            "sources": ["source_doc.pdf"],
            "retrieval_meta": {"score": 0.85}
        })
    db_pdf_chat["history_messages"].insert_many(history_messages)

    # config
    db_pdf_chat["config"].insert_one({
        "_id": ObjectId(),
        "key": "history_retention",
        "history_retention_days": 30,
        "updated_at": datetime.now()
    })

    # history
    pdf_histories = []
    for _ in range(5):
        pdf_histories.append({
            "_id": ObjectId(),
            "user_id": str(random.choice(users)["_id"]),
            "history_id": f"hist_{random.randint(1000,9999)}",
            "created_at": datetime.now(),
            "document_count": 2,
            "document_names": ["data1.pdf", "data2.pdf"],
            "latest_question_preview": "What is company policy?",
            "message_count": 4,
            "question_count": 2,
            "record_version": 1,
            "session_id": f"pdf_sess_{random.randint(100,999)}",
            "summary_upto_sequence": 4,
            "title": "Policy Chat Session",
            "updated_at": datetime.now()
        })
    db_pdf_chat["history"].insert_many(pdf_histories)

    # 7. mom - records
    mom_records = []
    for _ in range(12):
        u = random.choice(users)
        r_val = random.random()
        if r_val < 0.6:
            trans, summ, mom_st = "completed", "completed", "completed"
        elif r_val < 0.8:
            trans, summ, mom_st = "completed", "completed", "pending"
        elif r_val < 0.9:
            trans, summ, mom_st = "completed", "failed", "not_started"
        else:
            trans, summ, mom_st = "pending", "not_started", "not_started"

        mom_records.append({
            "_id": ObjectId(),
            "user_id": str(u["_id"]),
            "file_id": f"file_{random.randint(100,999)}",
            "created_at": random_date(30, 0),
            "date": "2026-07-10",
            "description": "Board meeting draft",
            "draft_status": "draft",
            "filename": "meeting.wav",
            "mom_docx": "/docs/mom.docx",
            "mom_file": "mom.docx",
            "mom_path": "/paths/mom",
            "mom_pdf": "/docs/mom.pdf",
            "mom_status": mom_st,
            "name": "Meeting Record",
            "requested_num_speakers": 3,
            "stored_filename": "stored_meeting.wav",
            "summary_docx": "/docs/summary.docx",
            "summary_file": "summary.docx",
            "summary_path": "/paths/summary",
            "summary_pdf": "/docs/summary.pdf",
            "summary_status": summ,
            "transcript_data": {},
            "transcript_docx": "/docs/transcript.docx",
            "transcript_pdf": "/docs/transcript.pdf",
            "transcription_file": "transcript.json",
            "transcription_status": trans,
            "unique_speakers": 3,
            "transcription_completed": trans == "completed",
            "summary_created": summ == "completed",
            "summary_exported": summ == "completed",
            "mom_created": mom_st == "completed",
            "mom_exported": mom_st == "completed",
            "transcript_exported": trans == "completed"
        })
    db_mom["records"].insert_many(mom_records)

    # 8. ai_services - doc_translation_history
    doc_trans_histories = []
    for _ in range(5):
        doc_trans_histories.append({
            "_id": ObjectId(),
            "user_id": str(random.choice(users)["_id"]),
            "history_id": f"dtrans_{random.randint(1000,9999)}",
            "created_at": datetime.now().isoformat(),
            "original_filename": "report_eng.docx",
            "output_api_path": "/api/download/report_es.docx",
            "output_filename": "report_es.docx",
            "src_lang": "en",
            "tgt_lang": "es",
            "title": "Monthly report translation"
        })
    db_services["doc_translation_history"].insert_many(doc_trans_histories)

    # 9. offline_chatbot - chat_sessions
    offline_chats = []
    for _ in range(10):
        u = random.choice(users)
        o_tool = random.choice(offline_gpt_tools)
        offline_chats.append({
            "_id": ObjectId(),
            "session_id": f"osess_{random.randint(100,999)}",
            "offline_gpt_id": str(o_tool["_id"]),
            "user_id": str(u["_id"]),
            "created_at": datetime.now().isoformat(),
            "latest_question_preview": "What is core business?",
            "question_count": 2,
            "title": "Offline chat query",
            "tool": "Local Llama2",
            "turns": [
                {"question": "How to operate offline?", "answer": "Use local database", "blocked": False, "asked_at": datetime.now().isoformat(), "answered_at": datetime.now().isoformat()}
            ],
            "updated_at": datetime.now().isoformat()
        })
    db_offline["chat_sessions"].insert_many(offline_chats)

    # 10. sandarbh - slide_deck_history
    db_sandarbh["slide_deck_history"].insert_one({
        "_id": ObjectId(),
        "user_id": str(users[0]["_id"]),
        "history_id": "sd_101",
        "created_at": datetime.now(),
        "download_pdf_api_path": "/api/download/deck.pdf",
        "download_pptx_api_path": "/api/download/deck.pptx",
        "job_id": "job_999",
        "pdf_path": "/slides/deck.pdf",
        "pptx_path": "/slides/deck.pptx",
        "preview_api_path": "/api/preview/deck",
        "title": "Q3 Sales deck"
    })

    # 11. scan_to_word - history
    db_scan["history"].insert_one({
        "_id": ObjectId(),
        "user_id": str(users[0]["_id"]),
        "history_id": "scan_101",
        "created_at": datetime.now(),
        "original_filename": "receipt.jpg",
        "output_api_path": "/api/download/receipt.docx",
        "output_file": "/docs/receipt.docx",
        "output_filename": "receipt.docx"
    })

    # 12. scanned_to_readable - history
    db_scanned["history"].insert_one({
        "_id": ObjectId(),
        "user_id": str(users[0]["_id"]),
        "history_id": "readable_101",
        "created_at": datetime.now(),
        "download_api_path": "/api/download/readable.pdf",
        "extracted_text": "Extracted readable document text content",
        "original_filename": "scanned_doc.pdf",
        "page_count": 5,
        "result_type": "searchable_pdf",
        "output_filename": "readable_doc.pdf"
    })

    # 13. summarization - history
    db_summ["history"].insert_one({
        "_id": ObjectId(),
        "user_id": str(users[0]["_id"]),
        "history_id": "summ_101",
        "created_at": datetime.now(),
        "download_api_path": "/api/download/summary.docx",
        "input_preview": "Very long essay text input preview...",
        "is_recursive": False,
        "original_filename": "essay.txt",
        "source_type": "text_input",
        "summary_text": "Short summary text context.",
        "summary_type": "executive_summary",
        "target_word_size": 250,
        "title": "Essay summary"
    })

    print("Dummy data generated successfully across all schema collections!")
