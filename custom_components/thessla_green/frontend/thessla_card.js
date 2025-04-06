class ThesslaPictureCard extends HTMLElement {
  setConfig(config) {
    this.innerHTML = `<ha-card><div style="padding: 1em;">Karta działa!</div></ha-card>`;
  }

  set hass(hass) {}

  getCardSize() {
    return 1;
  }
}

customElements.define("thessla-picture-card", ThesslaPictureCard);
