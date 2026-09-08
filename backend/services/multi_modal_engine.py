import os
from typing import Dict, Any, Optional, List, Union
from config import settings

class MultiModalRiskEngine:
    """
    Transparent Multi-Modal Livestock Health Risk Engine.
    Synthesizes:
      1. Image AI Risk Score (Vision screening)
      2. Symptom AI Risk Score (Clinical multi-disease screening)
      3. Environmental Risk Score (Geospatial / bioclimatic hazard)
      4. Health & Vaccination Context (Host susceptibility ledger)

    Uses fully configurable weights (defaults from settings) and enforces
    strict non-veterinary diagnosis disclaimers.
    """
    _instance: Optional["MultiModalRiskEngine"] = None

    def __init__(self):
        # Default weights from environment / configuration
        self.default_weights: Dict[str, float] = {
            "image": float(settings.RISK_WEIGHT_IMAGE),
            "symptoms": float(settings.RISK_WEIGHT_SYMPTOM),
            "environment": float(settings.RISK_WEIGHT_ENVIRONMENT),
            "context": float(settings.RISK_WEIGHT_CONTEXT)
        }
        self.threshold_low_max = float(settings.RISK_THRESHOLD_LOW_MAX)      # 30.0
        self.threshold_medium_max = float(settings.RISK_THRESHOLD_MEDIUM_MAX) # 60.0
        self.threshold_high_max = float(settings.RISK_THRESHOLD_HIGH_MAX)     # 80.0

    @classmethod
    def get_instance(cls) -> "MultiModalRiskEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def calculate_context_risk(
        self,
        vaccination_status: Optional[str] = "not_vaccinated",
        health_history: Optional[Union[str, List[str]]] = "none"
    ) -> Dict[str, Any]:
        """
        Evaluates animal host susceptibility based on immunization record and past clinical history.
        Returns a context risk score (0-100) and rationale.
        """
        # 1. Evaluate Vaccination Status Susceptibility
        vac_str = (vaccination_status or "not_vaccinated").strip().lower().replace(" ", "_")
        if vac_str in ["vaccinated", "up_to_date", "fully_vaccinated"]:
            vac_score = 5.0
            vac_desc = "Immunization is up-to-date, conferring substantial humoral protection."
        elif vac_str in ["partially_vaccinated", "single_dose"]:
            vac_score = 45.0
            vac_desc = "Incomplete vaccination regimen; partial protection with elevated vulnerability."
        elif vac_str in ["overdue", "booster_due"]:
            vac_score = 65.0
            vac_desc = "Booster vaccination overdue; antibody titers likely decayed below protective threshold."
        elif vac_str in ["not_vaccinated", "unvaccinated"]:
            vac_score = 85.0
            vac_desc = "Animal is completely unvaccinated; high biological susceptibility to viral/bacterial contagion."
        else:
            vac_score = 50.0
            vac_desc = f"Vaccination status '{vaccination_status}' is unverified; baseline susceptibility assumed."

        # 2. Evaluate Relevant Health History Predisposition
        history_items: List[str] = []
        if isinstance(health_history, list):
            history_items = [str(h).strip().lower() for h in health_history if str(h).strip()]
        elif isinstance(health_history, str):
            history_items = [h.strip().lower() for h in health_history.split(",") if h.strip()]

        history_score = 0.0
        history_desc_parts = []
        high_risk_keywords = ["lsd", "lumpy", "fmd", "foot and mouth", "anthrax", "brucellosis", "blackleg", "chronic", "recurrent"]
        moderate_risk_keywords = ["fever", "respiratory", "pneumonia", "mastitis", "weight_loss", "underweight", "immunosuppressed"]

        found_high = any(any(k in h for k in high_risk_keywords) for h in history_items)
        found_mod = any(any(k in h for k in moderate_risk_keywords) for h in history_items)
        is_clean = not history_items or any(h in ["none", "healthy", "nil", "no_prior_illness"] for h in history_items)

        if found_high:
            history_score = 80.0
            history_desc_parts.append("Documented prior severe/chronic infectious episodes or recurrent disease exposure.")
        elif found_mod:
            history_score = 50.0
            history_desc_parts.append("Documented past mild febrile/respiratory episodes indicating compromised baseline resistance.")
        elif is_clean:
            history_score = 5.0
            history_desc_parts.append("Clean clinical record with no reported prior chronic or epidemic illness.")
        else:
            history_score = 25.0
            history_desc_parts.append("Documented non-specific historical conditions.")

        # 3. Combine Vaccination (70% context weight) and History (30% context weight)
        context_score = (0.70 * vac_score) + (0.30 * history_score)
        context_score = max(0.0, min(100.0, float(round(context_score, 1))))
        combined_desc = f"{vac_desc} {' '.join(history_desc_parts)}"

        return {
            "context_score": context_score,
            "vaccination_score": vac_score,
            "history_score": history_score,
            "description": combined_desc
        }

    def evaluate(
        self,
        image_risk_score: Optional[float] = None,
        symptom_risk_score: Optional[float] = None,
        environmental_risk_score: Optional[float] = None,
        vaccination_status: Optional[str] = "not_vaccinated",
        health_history: Optional[Union[str, List[str]]] = "none",
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Executes multi-modal weighted livestock health risk assessment.
        Ensures transparent factor accounting, dynamic weight renormalization if modalities
        are missing, and explicit non-diagnostic advisory metadata.
        """
        # 1. Resolve Weights (Custom overrides or configured defaults)
        weights = dict(self.default_weights)
        if custom_weights:
            for k, v in custom_weights.items():
                if k in weights and v is not None and v >= 0.0:
                    weights[k] = float(v)

        # 2. Compute Context Risk
        context_eval = self.calculate_context_risk(vaccination_status, health_history)
        context_score = context_eval["context_score"]

        # 3. Determine Active Modalities & Dynamic Renormalization
        active_modalities = {}
        if image_risk_score is not None:
            active_modalities["image"] = max(0.0, min(100.0, float(image_risk_score)))
        if symptom_risk_score is not None:
            active_modalities["symptoms"] = max(0.0, min(100.0, float(symptom_risk_score)))
        if environmental_risk_score is not None:
            active_modalities["environment"] = max(0.0, min(100.0, float(environmental_risk_score)))
        # Context is always present
        active_modalities["context"] = context_score

        # Renormalize active weights to sum exactly to 1.0 (100%)
        active_weight_sum = sum(weights[k] for k in active_modalities.keys())
        if active_weight_sum <= 0.0:
            # Fallback to equal weighting if zero
            effective_weights = {k: 1.0 / len(active_modalities) for k in active_modalities.keys()}
        else:
            effective_weights = {k: weights[k] / active_weight_sum for k in active_modalities.keys()}

        # 4. Calculate Final Weighted Risk Score
        final_score = 0.0
        for k, score in active_modalities.items():
            final_score += score * effective_weights[k]
        final_score = float(round(max(0.0, min(100.0, final_score)), 1))

        # 5. Classify Risk Level According to Specification:
        # 0-30: Low
        # 31-60: Medium
        # 61-80: High
        # 81-100: Critical
        if final_score <= self.threshold_low_max:
            risk_level = "Low"
        elif final_score <= self.threshold_medium_max:
            risk_level = "Medium"
        elif final_score <= self.threshold_high_max:
            risk_level = "High"
        else:
            risk_level = "Critical"

        # 6. Build Granular Contributing Factors Breakdown
        factor_metadata = {
            "image": {
                "name": "Image AI Risk",
                "desc_func": lambda s: (
                    f"Visual computer vision screening detected significant skin lesions/nodules ({s:.1f}/100)."
                    if s >= 60.0 else
                    f"Visual screening shows minor or inconclusive dermatological irregularities ({s:.1f}/100)."
                    if s >= 30.0 else
                    f"Visual screening indicates clear skin with no distinctive epidemic lesions ({s:.1f}/100)."
                )
            },
            "symptoms": {
                "name": "Symptom AI Risk",
                "desc_func": lambda s: (
                    f"Reported acute clinical symptoms strongly match infectious disease profiles ({s:.1f}/100)."
                    if s >= 60.0 else
                    f"Reported mild or non-specific clinical signs ({s:.1f}/100)."
                    if s >= 30.0 else
                    f"No significant pathognomonic symptoms reported ({s:.1f}/100)."
                )
            },
            "environment": {
                "name": "Environmental Risk",
                "desc_func": lambda s: (
                    f"High regional vector-breeding suitability and dense host geography ({s:.1f}/100)."
                    if s >= 60.0 else
                    f"Moderate ambient humidity/temperature favorable for vector survival ({s:.1f}/100)."
                    if s >= 30.0 else
                    f"Low environmental transmission hazard in this geographical area ({s:.1f}/100)."
                )
            },
            "context": {
                "name": "Health/Vaccination Context",
                "desc_func": lambda s: f"{context_eval['description']} (Context score: {s:.1f}/100)."
            }
        }

        contributing_factors = []
        for k, score in active_modalities.items():
            eff_w = effective_weights[k]
            contribution = round(score * eff_w, 2)
            pct_of_total = round((contribution / final_score) * 100.0, 1) if final_score > 0 else 0.0
            meta = factor_metadata[k]
            contributing_factors.append({
                "factor": meta["name"],
                "modality_key": k,
                "raw_score": score,
                "weight": round(eff_w, 4),
                "weighted_contribution": contribution,
                "percentage_of_total_risk": pct_of_total,
                "description": meta["desc_func"](score)
            })

        # Sort descending by weighted contribution so primary drivers appear first
        contributing_factors.sort(key=lambda x: x["weighted_contribution"], reverse=True)

        return {
            "final_risk_score": final_score,
            "risk_level": risk_level,
            "contributing_factors": contributing_factors,
            "individual_model_scores": {
                "image_risk": active_modalities.get("image", None),
                "symptom_risk": active_modalities.get("symptoms", None),
                "environmental_risk": active_modalities.get("environment", None),
                "context_risk": active_modalities.get("context", None)
            },
            "risk_thresholds": {
                "Low": f"0-{int(self.threshold_low_max)}",
                "Medium": f"{int(self.threshold_low_max)+1}-{int(self.threshold_medium_max)}",
                "High": f"{int(self.threshold_medium_max)+1}-{int(self.threshold_high_max)}",
                "Critical": f"{int(self.threshold_high_max)+1}-100"
            },
            "calculation_details": {
                "configured_weights": {k: round(v, 4) for k, v in weights.items()},
                "effective_weights": {k: round(v, 4) for k, v in effective_weights.items()},
                "active_modalities_count": len(active_modalities),
                "is_dynamically_renormalized": active_weight_sum != 1.0 or len(active_modalities) < 4,
                "formula": "final_risk_score = sum(raw_score_i * effective_weight_i)"
            },
            # Mandatory Ethical Non-Diagnosis Disclaimer
            "is_veterinary_diagnosis": False,
            "disclaimer": (
                "This score is an AI-assisted multi-modal risk assessment tool and NOT a veterinary diagnosis. "
                "It synthesizes visual computer vision triage, reported symptoms, geospatial vector risk, and immunization history "
                "to provide early warning triage for farmers and veterinarians. "
                "Clinical decisions, prescriptions, and statutory quarantine actions must be confirmed by a licensed veterinarian."
            )
        }

def get_multi_modal_engine() -> MultiModalRiskEngine:
    return MultiModalRiskEngine.get_instance()
