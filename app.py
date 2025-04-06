from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = FastAPI(title="FlavorDB Molecule API")

# Scraper function
def get_flavor_molecules(entity_id: int):
    url = f"https://cosylab.iiitd.edu.in/flavordb2/entity_details?id={entity_id}"
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=404, detail=f"Entity ID {entity_id} not found")

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find("table", {"id": "molecules"})

    if not table:
        raise HTTPException(status_code=404, detail=f"Molecule table not found for entity {entity_id}")

    rows = table.find("tbody").find_all("tr")
    data = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 3:
            continue
        common_name = cols[0].text.strip()
        pubchem_id = cols[1].text.strip()
        flavor_profile = cols[2].text.strip()
        pubchem_link = cols[1].find("a")["href"] if cols[1].find("a") else ""
        data.append({
            "compound": common_name,
            "pubchem_id": pubchem_id,
            "flavor_profile": flavor_profile,
            "pubchem_link": pubchem_link
        })

    return data

# FastAPI route
@app.get("/flavor-molecules/{entity_id}", response_class=JSONResponse)
def get_molecules(entity_id: int):
    try:
        molecules = get_flavor_molecules(entity_id)
        return {"entity_id": entity_id, "molecules": molecules}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))