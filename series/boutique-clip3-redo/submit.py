"""Redo of the boutique clip 3 (auto-loop seq, seed 646707790 -> 646707791).

Two fixes over the original:

1. THE CARD IS GONE ENTIRELY. The original had the card stick to the gown.
   Attempt two moved it to the sales counter and negated the failure by name —
   and it STILL magnetised onto the dress. When a prop misrenders twice,
   removing the prop beats describing it harder. The card, wallet, cash and
   phone are now all forbidden and Mara's hands stay empty for the whole shot;
   the physical beat is carried by her shifting the tote and turning to leave.
   The card was vestigial anyway: it was proof-of-money left over from the old
   money ending, and the ending is no longer about money.

2. THE ENDING WAS PURE MONEY. "That one. And the coat beside it." proves she
   can afford it and costs Claire nothing. Per the §0 consequence rule, the
   ending now TAKES THE SALE AWAY — the past tense ("I was going to take both")
   tells Claire the sale existed and is gone, and the gesture is Mara leaving
   rather than flashing anything.

Chained off clip 2's last frame with mode "firstlast", exactly as the original
clip 3 was, so the continuity is preserved.
"""
import json
import urllib.request

PROMPT = """integrated_multimodal_description: [Single continuous 8-second shot] Continue immediately in the exact same designer boutique, same lighting, same framing, no time has passed. Both characters stand near the lit glass window display case holding the ivory silk dress, with the dark wool coat on a stand directly beside it. Grounded realistic acting. This clip ends on the reveal and cuts hard.

There are exactly two visible adult characters.

CLAIRE is a 29-year-old shop assistant, slim, fair skin, sleek dark hair in a tight low bun, minimal makeup, all-black tailored uniform dress with a thin gold name badge, crisp clipped polite voice. She stands slightly behind and below Mara.

MARA is a 41-year-old woman, warm brown skin, hair tied back plainly, no makeup, faded supermarket-brand zip-up fleece, plain jeans, worn trainers, canvas tote over one shoulder. Completely calm throughout, never raises her voice, never smiles in triumph, never looks smug.

Both speak natural conversational English.

CRITICAL AUDIO RULE:
There is NO narrator.
There is NO voice-over.
ONLY dialogue written inside <d>...</d> may be spoken aloud.
Everything outside <d>...</d> is SILENT visual direction only.

CRITICAL DIALOGUE PRESERVATION:
Speak every <d> line EXACTLY as written.
Do NOT paraphrase, soften, or rewrite the dialogue.

CRITICAL PROP RULE:
NO payment card appears in this clip at any point. No credit card, no bank card, no wallet, no purse, no cash, no cheque, no phone, and no receipt. Mara does NOT reach into her pockets and does NOT take anything out.
Mara's hands stay empty and visible for the entire shot.
Nothing is placed on, stuck to, pinned to, or held against the ivory dress, the wool coat, the coat stand, the mannequin, or the glass of the display case.
No price tags, labels or any readable text are visible anywhere in frame.

IMPORTANT EYELINE LOCK:
Claire and Mara face each other at a natural three-quarter angle. They speak directly to each other's faces. Neither character looks toward or acknowledges the camera. The camera sits at a 30-40 degree side angle, not directly in front of either character. No fourth-wall breaking.

[0.0-0.4s] Continue mid-conversation with no pause or reset.

[0.4-3.0s] Claire, polite and firm (S1): <d>[English] I'd rather not take it out of the window unless you're serious.</d>

[3.0-4.8s] Mara, flat and matter-of-fact, eyes on Claire (S2): <d>[English] I was going to take both. The dress and the coat.</d>

[4.8-6.2s] Mara shifts the canvas tote higher onto her shoulder with one hand and turns her body a quarter step toward the shop door, unhurried. Her hands remain empty.

[6.2-8.0s] Mara, quiet and matter-of-fact, not looking back (S2): <d>[English] I'll find somewhere that would have shown me.</d>

[7.8-8.0s] Claire's face falls. Her mouth opens very slightly. She does not get to speak.

CUT IMMEDIATELY at 8.0 seconds.

Do not show Claire apologising. Do not show Claire replying. Do not show any other staff, customers, or onlookers. Do not add applause, reaction shots, or a manager. Do not let Mara smirk, gloat, or celebrate. Do not have Mara buy anything. Do not have Claire take the dress out of the window.

Speaker lock: Only Claire, the shop assistant in black, speaks S1. Only Mara, the woman in the fleece, speaks S2. Never swap dialogue, voices, lip movements, or eyelines. No other voices are present.

Camera: Single continuous medium close two-shot from a slight side angle, framed slightly low so Mara remains visually above Claire, pushing in with small amplitude at slow speed toward Mara across the second half of the shot. No cuts.

overall_soundscape: Quiet boutique room tone with a faint air-conditioning hum and distant muffled street traffic through glass. Light fabric movement from the fleece as the tote is shifted on her shoulder, a single soft footstep as she turns toward the door, and one short intake of breath from the assistant at the end.

non_diegetic_music: None."""

PAYLOAD = {
    "prompt": PROMPT,
    "mode": "firstlast",
    "engine": "vpipe",
    "params": {"width": 576, "height": 1024, "frames": 192, "steps": 8,
               "reuse": 2, "layers": 40, "seed": 646707792, "ssd_streaming": True},
    "first_frame": "boutique-clip2-last.jpg",
}

if __name__ == "__main__":
    req = urllib.request.Request(
        "http://127.0.0.1:7833/api/generate", data=json.dumps(PAYLOAD).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        print(resp.status, resp.read().decode())
