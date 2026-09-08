# Environmental & Geospatial Risk Engine (`ml/environmental_risk`)

This module quantifies regional environmental and vector-breeding risk multipliers for vector-borne livestock diseases such as **Lumpy Skin Disease (LSD)** and **Foot-and-Mouth Disease (FMD)**.

## Scientific Basis
- **Vector Transmission**: LSD is primarily transmitted mechanically by biting arthropods (*Stomoxys calcitrans*, *Aedes aegypti*, and *Rhipicephalus* ticks).
- **Meteorological Predictors**:
  - *Temperature*: Optimal vector activity occurs between $24^\circ\text{C}$ and $35^\circ\text{C}$.
  - *Relative Humidity*: Sustained humidity $>70\%$ sharply increases tick and mosquito larval development rates.
  - *Precipitation*: Rainfall $>5\text{ mm}$ produces stagnant pooling necessary for breeding cycles.
- **Output**: Returns an `environmental_risk_score` ($0.0 - 100.0$) and a risk category (`LOW`, `MODERATE`, `HIGH`) to augment animal-level health assessments.
