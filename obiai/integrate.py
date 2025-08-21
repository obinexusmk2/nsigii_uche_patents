
#!/usr/bin/env python3
"""Glue script: run a coordinate-aware OBIAI decision on a toy medical input."""
from obiai.ontology import Identity
from obiai.medical import MedicalDiagnosisAgent

def main():
    agent = MedicalDiagnosisAgent(identity=Identity(0.8, 0.9, 0.6))
    observation = {"abc": 1}  # placeholder features
    demographic = {"skin_tone": "V", "bias_phi": 1.1}
    out = agent.diagnose(observation, demographic)

    print("MODE=", out.mode)
    print("OCM=", round(out.ocm, 3))
    print("IDENTITY=", out.identity)
    print("POSTERIOR=", [(h.id, round(h.p, 3)) for h in out.posterior])
    print("AUDIT=", out.audit)

if __name__ == "__main__":
    main()
