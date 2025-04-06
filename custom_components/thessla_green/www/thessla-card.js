class ThesslaCard extends HTMLElement {
    set hass(hass) {
      const entityId = this.config.entity;
      const state = hass.states[entityId]?.state;
  
      this.innerHTML = `
        <ha-card header="Thessla Green">
          <div class="card-content">
            Temperatura: ${state} °C
          </div>
        </ha-card>
      `;
    }
  
    setConfig(config) {
      this.config = config;
    }
  
    getCardSize() {
      return 1;
    }
  }
  
  customElements.define('thessla-card', ThesslaCard);  