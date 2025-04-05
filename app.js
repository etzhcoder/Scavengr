const map = L.map("map").setView([37.8, -96], 4);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap",
}).addTo(map);

let marker; // reuse the same pin so the map stays clean

///////////////////////  Click handler  ///////////////////////
map.on("click", async (e) => {
  const { lat, lng } = e.latlng;

  // drop / move the pin
  if (marker) marker.setLatLng(e.latlng);
  else marker = L.marker(e.latlng).addTo(map);

  // ask the camper what they packed
  const brought = prompt(
    "Comma‑separated list of ingredients you brought with you:"
  );
  if (brought === null) return; // user hit Cancel

  // show a loading message in the Recipes panel
  const box = document.getElementById("recipes");
  box.textContent = "Thinking…";

  // POST the data to our Flask endpoint
  try {
    const r = await fetch("http://127.0.0.1:5000/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lat, lng, brought }),
    });

    const txt = await r.text();
    box.textContent = txt;
  } catch (err) {
    box.textContent = "Error: " + err;
  }
});