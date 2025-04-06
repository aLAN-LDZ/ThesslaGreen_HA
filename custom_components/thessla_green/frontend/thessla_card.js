class ThesslaPictureCard extends HTMLElement {
    setConfig(config) {
      this._config = config;
  
      const content = document.createElement("hui-picture-elements-card");
      content.setConfig({
        image: "/custom_components/thessla_green/frontend/reku.png",
        elements: [
          {
            type: "state-badge",
            entity: "binary_sensor.remote_ui",
            style: {
              top: "32%",
              left: "40%"
            }
          }
        ]
      });
  
      const card = document.createElement("ha-card");
      card.appendChild(content);
      this.innerHTML = "";
      this.appendChild(card);
    }
  
    set hass(hass) {
      this._hass = hass;
      if (this.firstChild && this.firstChild.firstChild) {
        this.firstChild.firstChild.hass = hass;
      }
    }
  
    getCardSize() {
      return 3;
    }
  }
  
  customElements.define("thessla-picture-card", ThesslaPictureCard);  