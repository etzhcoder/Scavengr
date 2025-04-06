const map = L.map("map").setView([37.8, -96], 4);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap",
    }).addTo(map);

    let marker; // reuse the same pin

    // Retrieve the universal ingredient list from localStorage
    function getIngredients() {
        const stored = localStorage.getItem('campingIngredients');
        return stored ? JSON.parse(stored) : [];
      }
      
      // Retrieve preferences from localStorage (if any)
      function getPreferences() {
        return localStorage.getItem('campingPreferences') || "";
      }
      
      // On map click, use the stored ingredients and preferences.
      map.on("click", async (e) => {
        const { lat, lng } = e.latlng;
      
        // Drop or move the marker.
        if (marker) {
          marker.setLatLng(e.latlng);
        } else {
          marker = L.marker(e.latlng).addTo(map);
        }
      
        // Get the ingredients and preferences
        const ingredients = getIngredients();
        const brought = ingredients.join(', ');
        const preferences = getPreferences();
      
        // Show a loading message in the recipes panel.
        const box = document.getElementById("recipes");
        box.textContent = "Thinking…";
      
        // POST the data (including preferences) to the /generate endpoint.
        try {
          const r = await fetch("http://127.0.0.1:5000/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ lat, lng, brought, preferences }),
          });
          const txt = await r.text();
          box.innerHTML = txt;
        } catch (err) {
          box.innerHTML = "Error: " + err;
        }
      });