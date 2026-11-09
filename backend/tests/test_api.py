import time


def test_health(client):
    assert client.get("/api/health").json()["status"] == "ok"


def test_config_lists_assets(client):
    body = client.get("/api/config").json()
    assert body["groqConfigured"] is False
    assert len(body["backgrounds"]) > 0
    assert any(f["id"] == "Montserrat/Montserrat-ExtraBold.ttf" for f in body["fonts"])
    assert {a["key"] for a in body["aspectRatios"]} == {"4:5", "9:16", "1:1", "16:9", "4:3"}


def test_thumbnail(client):
    bg = client.get("/api/config").json()["backgrounds"][0]
    res = client.get(bg["thumbnailUrl"])
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/jpeg"


def test_preview_returns_data_uri(client):
    res = client.post(
        "/api/render/preview",
        json={
            "quote": "Waste no more time arguing what a good man should be. Be one.",
            "author": "Marcus Aurelius",
            "aspectRatio": "9:16",
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["image"].startswith("data:image/jpeg;base64,")
    assert (body["width"], body["height"]) == (1080, 1920)


def test_post_lifecycle(client):
    res = client.post("/api/render/post", json={"quote": "Be here.", "caption": "Hi #now"})
    assert res.status_code == 201, res.text
    item = res.json()
    assert item["kind"] == "post" and item["quote"] == "Be here."
    assert client.get(item["url"]).status_code == 200

    listed = client.get("/api/media", params={"kind": "post"}).json()
    assert [i["filename"] for i in listed] == [item["filename"]]

    assert client.delete(f"/api/media/post/{item['filename']}").status_code == 204
    assert client.get("/api/media").json() == []


def test_video_is_h264_mp4(client):
    res = client.post(
        "/api/render/video",
        json={"quote": "Still waters.", "duration": 2, "fadeIn": 0.5, "fadeOut": 0.5},
    )
    assert res.status_code == 201, res.text
    data = client.get(res.json()["url"]).content
    assert data[4:8] == b"ftyp" and b"avc1" in data[:4096]


def test_video_rejects_fades_longer_than_duration(client):
    res = client.post(
        "/api/render/video", json={"quote": "x y", "duration": 2, "fadeIn": 2, "fadeOut": 1}
    )
    assert res.status_code == 422


def test_delete_rejects_path_traversal(client):
    assert client.delete("/api/media/post/..%5C..%5Cpyproject.toml").status_code == 404


def test_ai_without_key_is_a_clear_error(client):
    res = client.post("/api/ai/quote", json={"theme": "Time"})
    assert res.status_code == 400
    assert "Groq API key" in res.json()["detail"]


def test_manual_batch_renders_posts(client):
    res = client.post(
        "/api/batches",
        json={
            "kind": "post",
            "count": 2,
            "quoteSource": "manual",
            "quote": "Again.",
            "withCaptions": False,
        },
    )
    assert res.status_code == 202, res.text
    job_id = res.json()["id"]
    for _ in range(100):
        job = client.get(f"/api/batches/{job_id}").json()
        if job["status"] in ("completed", "failed"):
            break
        time.sleep(0.1)
    assert job["status"] == "completed", job
    assert job["completed"] == 2
    assert len({i["background"] for i in job["items"]}) == 2
