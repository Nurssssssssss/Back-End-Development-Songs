# Back-End-Development-Songs

Flask Songs API for the IBM Python Back-end capstone. Routes `GET /health`, `GET /count`, `GET /song`, `GET /song/<id>`, `POST /song`, `PUT /song/<id>`, `DELETE /song/<id>`.

```bash
python -m pip install -r requirements.txt
python -m pytest -v
python app.py
```

Uses deterministic seeded in-memory records for local demonstration. **For full original IBM MongoDB requirements**, set `MONGO_URI=mongodb://host:27017`, `MONGO_DB=songs`, `SEED_MONGO=1` (only seeds an empty collection). In IBM Cloud/OpenShift use `MONGODB_SERVICE` and optional `MONGODB_USERNAME`, `MONGODB_PASSWORD`. Do not expose credentials in public repositories.

The course sample expects `GET /song` to return a JSON object with `songs`, and successful `DELETE` to return HTTP 204.
