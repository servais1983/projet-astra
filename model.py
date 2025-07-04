# model.py
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

print("Initialisation du modèle local Phi-3...")

# Le modèle sera téléchargé une seule fois puis stocké en cache local
model_name = "microsoft/Phi-3-mini-4k-instruct"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto", # Utilise le GPU si disponible
    trust_remote_code=True,
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Création du pipeline pour la génération de texte
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
)

def ask_phi(prompt_text):
    """
    Fonction pour interroger le modèle Phi-3 localement.
    Toute notre logique d'IA passera par ici pour garantir la confidentialité.
    """
    messages = [
        {"role": "user", "content": prompt_text},
    ]

    generation_args = {
        "max_new_tokens": 500,
        "return_full_text": False,
        "temperature": 0.7,
        "do_sample": True,
    }

    output = pipe(messages, **generation_args)
    return output[0]['generated_text']

print("Modèle Phi-3 prêt et opérationnel en local.")

if __name__ == '__main__':
    # Test rapide pour vérifier que tout fonctionne
    response = ask_phi("Explique le concept de 'Jamming' dans le contexte des communications satellite.")
    print("\n--- Test du modèle ---")
    print(f"Réponse de Phi-3 : {response}")
    print("--------------------") 