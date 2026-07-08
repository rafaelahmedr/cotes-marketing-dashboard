# Cotes Campaign Analytics — Streamlit App

## What this is
A Streamlit dashboard that reads your Funnel Excel export and gives you
interactive campaign performance views across Google Ads, Meta, and LinkedIn,
with fast filtering and visual performance trends.

It also includes an in-app **Export PDF Report** button that downloads a
summary of the currently filtered view.

## Local setup (5 minutes)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open http://localhost:8501 in your browser and upload your Funnel Excel file.

## Streamlit Community Cloud deployment

1. Push this repo to GitHub (private repo is fine)
2. Go to share.streamlit.io → New app → connect your repo
3. Set main file to `app.py`
4. Deploy — done

No secrets needed for the file-upload version.

## Connecting directly to SharePoint (optional upgrade)

If you want the app to auto-load the latest file from SharePoint without
manual upload, you need two things:

### Step 1 — Register an Azure AD app (ask your M365 admin, ~15 mins)
1. Go to portal.azure.com → Azure Active Directory → App registrations → New
2. Name it "Cotes Analytics App"
3. Under API permissions → Add → Microsoft Graph → Application permissions:
   - Files.Read.All
   - Sites.Read.All
4. Grant admin consent
5. Create a Client Secret (Certificates & secrets → New client secret)
6. Note down: Tenant ID, Client ID, Client Secret

### Step 2 — Add secrets to Streamlit Cloud
In your app settings on share.streamlit.io → Secrets:

```toml
[sharepoint]
tenant_id     = "your-tenant-id"
client_id     = "your-client-id"
client_secret = "your-client-secret"
site_hostname = "yourcompany.sharepoint.com"
site_path     = "/sites/Marketing"
file_path     = "/Shared Documents/Funnel/campaign_data.xlsx"
```

### Step 3 — Replace the file uploader with this code block
```python
import requests, msal
from io import BytesIO

def load_from_sharepoint():
    cfg = st.secrets["sharepoint"]
    app = msal.ConfidentialClientApplication(
        cfg["client_id"],
        authority=f"https://login.microsoftonline.com/{cfg['tenant_id']}",
        client_credential=cfg["client_secret"],
    )
    token = app.acquire_token_for_client(["https://graph.microsoft.com/.default"])
    headers = {"Authorization": f"Bearer {token['access_token']}"}

    # Resolve site ID from hostname + site path
    site_url = (
        f"https://graph.microsoft.com/v1.0/sites/"
        f"{cfg['site_hostname']}:{cfg['site_path']}"
    )
    site_resp = requests.get(site_url, headers=headers)
    site_resp.raise_for_status()
    site_id = site_resp.json()["id"]

    # Download file content via Graph API
    file_url = (
        f"https://graph.microsoft.com/v1.0/sites/{site_id}/"
        f"drive/root:{cfg['file_path']}:/content"
    )
    r = requests.get(file_url, headers=headers)
    r.raise_for_status()
    return BytesIO(r.content)
```

## Data format expected
One sheet, daily rows, columns:
Date | Month | Year | Traffic source | Campaign | Media type | Paid / Organic | Currency | Cost (*) | Clicks | CPC (*) | CPM (*) | CTR | Impressions

Exactly what Funnel exports today — no changes needed.

## Adding conversions / ROAS
In Funnel, add the Conversions and Conversion Value columns to your export.
The app will need two new lines in the aggregation section — ask for the update
when you have those columns available.
