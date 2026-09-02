const BANQUE_NIVEAUX = Array.isArray(window.BANQUE_NIVEAUX) ? window.BANQUE_NIVEAUX : [];
const CLE_SAUVEGARDE_NIVEAU = 'pedantox_campagne_idx';

let niveauActuelIdx = 0;

let niveauDonnees = null;



let motsTrouvesSet = new Set();

let historiqueEssais = [];

let motsDuTitre = [];

let motsDuTexte = [];

let jeuGagne = false;

let motsClesDuTitreSolution = [];

let motsSimilairesTrouves = new Map();



function lireNiveauSauvegarde() {

    try {

        return localStorage.getItem(CLE_SAUVEGARDE_NIVEAU);

    } catch (error) {

        return null;

    }

}



function sauvegarderNiveau(indexNiveau) {

    try {

        localStorage.setItem(CLE_SAUVEGARDE_NIVEAU, indexNiveau);

    } catch (error) {

        // Le jeu doit rester utilisable meme si le navigateur bloque localStorage.

    }

}



function notifier(message, type = 'error') {

    const toast = document.getElementById('toastNotification');

    const iconEl = document.getElementById('toastIcon');

    const msgEl = document.getElementById('toastMessage');



    iconEl.textContent = type === 'error' ? '⚠️' : '💡';

    msgEl.textContent = message;



    toast.classList.add('show');

    setTimeout(() => {

        toast.classList.remove('show');

    }, 3200);

}



function normaliserMot(mot) {

    return mot.toLowerCase()

        .normalize("NFD")

        .replace(/[\u0300-\u036f]/g, "")

        .replace(/[^a-zA-Z0-9]/g, "");

}



function decouperTexte(texte) {

    const regex = /[a-zA-Z0-9À-ÿœŒæÆÇḉ̀̂̈̌åÅøØ]+|\s+|./g;

    const morceaux = texte.match(regex) || [];



    return morceaux.map(morceau => {

        if (morceau.trim() === '') {

            return { type: 'space', texte: morceau };

        }



        const motNettoye = normaliserMot(morceau);

        if (motNettoye.length > 0) {

            return { type: 'word', texteOriginal: morceau, motNettoye: motNettoye };

        } else {

            return { type: 'punctuation', texte: morceau };

        }

    });

}



function chargerNiveau() {

    if (BANQUE_NIVEAUX.length === 0) {

        notifier("Les niveaux n'ont pas pu être chargés.");

        return;

    }

    if (niveauActuelIdx >= BANQUE_NIVEAUX.length) {

        niveauActuelIdx = 0;

    }



    niveauDonnees = BANQUE_NIVEAUX[niveauActuelIdx];

    motsTrouvesSet = new Set();

    historiqueEssais = [];

    jeuGagne = false;

    motsSimilairesTrouves = new Map();



    document.getElementById('levelIndicator').textContent = `Niveau ${niveauActuelIdx + 1} / ${BANQUE_NIVEAUX.length}`;

    const progressionPourcent = Math.max(0, Math.min(100, Math.round((niveauActuelIdx / BANQUE_NIVEAUX.length) * 100)));

    document.getElementById('progressBarFill').style.width = `${progressionPourcent}%`;

    document.getElementById('percentIndicator').textContent = `${progressionPourcent}%`;



    document.getElementById('victoryMessage').classList.add('hidden');

    document.getElementById('wordInput').disabled = false;

    document.getElementById('btnSubmit').disabled = false;

    document.getElementById('nbTentatives').innerText = "0";

    document.getElementById('motsTrouves').innerText = "0";

    document.getElementById('historyBody').innerHTML = "";

    document.getElementById('wordInput').value = '';

    document.getElementById('wordInput').focus();



    const motsSolutionBruts = niveauDonnees.titre.match(/[a-zA-Z0-9À-ÿ]+/g) || [];

    motsClesDuTitreSolution = motsSolutionBruts.map(normaliserMot).filter(m => m.length > 0);



    motsDuTitre = decouperTexte(niveauDonnees.titre);

    motsDuTexte = decouperTexte(niveauDonnees.texte);



    rendreLeTexte();

}



function genererHtmlMots(tableauMots, elementCible) {

    elementCible.innerHTML = '';

    tableauMots.forEach(item => {

        if (item.type === 'space' || item.type === 'punctuation') {



            elementCible.appendChild(document.createTextNode(item.texte));

        } else if (item.type === 'word') {

            const span = document.createElement('span');

            span.classList.add('word-block');

            const motSimilaire = Array.from(motsSimilairesTrouves.entries()).find(([input, cible]) => cible === item.motNettoye);

            if (motsTrouvesSet.has(item.motNettoye) || jeuGagne) {

                span.textContent = item.texteOriginal;

                span.classList.add('revealed-word');

            } else {
                let motTapeParUtilisateur = null;
                for (const [input, cible] of motsSimilairesTrouves.entries()) {
                  if (cible === item.motNettoye) {
                    motTapeParUtilisateur = input;
                    break;
                  }
                }

                if (motTapeParUtilisateur) {
                  span.textContent = motTapeParUtilisateur; 
                  span.classList.add("similar-word");
                } else {
                  span.textContent = "■".repeat(item.texteOriginal.length);
                  span.style.color = "transparent";
                  span.classList.add("hidden-word");
                  span.dataset.count = item.texteOriginal.length;
                }
            }

            elementCible.appendChild(span);

        }

    });

}



function rendreLeTexte() {

    genererHtmlMots(motsDuTitre, document.getElementById('titleZone'));

    genererHtmlMots(motsDuTexte, document.getElementById('bodyZone'));

}



function verifierMot(event) {

    if(event) event.preventDefault();

    if(jeuGagne) return;



    const input = document.getElementById('wordInput');

    const motSaisi = input.value.trim();

    if (!motSaisi) return;



    const motNormalise = normaliserMot(motSaisi);

    input.value = '';



    if (historiqueEssais.some(e => e.mot === motNormalise)) {

        notifier("Vous avez déjà testé ce mot !");

        return;

    }



    let listeMotsAValider = [motNormalise];

    if (niveauDonnees.variantes) {

        for (let motCle in niveauDonnees.variantes) {

            const variantes = niveauDonnees.variantes[motCle].map(normaliserMot);

            if (variantes.includes(motNormalise)) {

                listeMotsAValider.push(motCle);

            }

        }

    }

    const sim = niveauDonnees.similarities || {};
    for (const [cible, synonymes] of Object.entries(sim)) {
        if (synonymes.map(normaliserMot).includes(motNormalise)) {
            motsSimilairesTrouves.set(motNormalise, cible);
        }
    }

    let occurrencesTotales = 0;

    const motsTrouvesDansCetteSaisie = new Set();



    listeMotsAValider.forEach(motDeLaListe => {

        let trouveDansTitre = false;

        let trouveDansTexte = false;



        motsDuTitre.forEach(item => {

            if (item.type === 'word' && item.motNettoye === motDeLaListe) {

                occurrencesTotales++;

                trouveDansTitre = true;

            }

        });



        motsDuTexte.forEach(item => {

            if (item.type === 'word' && item.motNettoye === motDeLaListe) {

                occurrencesTotales++;

                trouveDansTexte = true;

            }

        });



        if (trouveDansTitre || trouveDansTexte || motsClesDuTitreSolution.includes(motDeLaListe)) {

            motsTrouvesDansCetteSaisie.add(motDeLaListe);

        }

    });



    motsTrouvesDansCetteSaisie.forEach(mot => motsTrouvesSet.add(mot));



    historiqueEssais.unshift({ mot: motSaisi, occurrences: occurrencesTotales });



    document.getElementById('nbTentatives').innerText = historiqueEssais.length;

    document.getElementById('motsTrouves').innerText = motsTrouvesSet.size;



    rendreLeTexte();

    mettreAJourHistorique();

    verifierVictoire();

}



function donnerIndices() {

    const indicesDisponibles = niveauDonnees.indices.map(normaliserMot).filter(mot => !motsTrouvesSet.has(mot));

    if (indicesDisponibles.length === 0) {

        notifier("Plus d'indices disponibles pour cette session !");

        return;

    }

    const motIndice = indicesDisponibles[Math.floor(Math.random() * indicesDisponibles.length)];

    motsTrouvesSet.add(motIndice);



    historiqueEssais.unshift({ mot: `💡 Indice: ${motIndice}`, occurrences: "Bonus" });

    rendreLeTexte();

    mettreAJourHistorique();

    verifierVictoire();

    notifier(`Indice révélé : ${motIndice}`, 'info');

}



function verifierVictoire() {



    const aTrouveToutLeTitre = motsClesDuTitreSolution.every(motCle => motsTrouvesSet.has(motCle));



    if (aTrouveToutLeTitre && !jeuGagne) {

        jeuGagne = true;



        const isDernierNiveau = (niveauActuelIdx === BANQUE_NIVEAUX.length - 1);

        const textVictoire = document.getElementById('victoryText');

        const btnSuivant = document.getElementById('btnNextLevel');



        if (isDernierNiveau) {

            textVictoire.textContent = `FÉLICITATIONS!`;

            btnSuivant.textContent = "Recommencer au Début 🔄";

        } else {

            textVictoire.textContent = `La solution était bien : "${niveauDonnees.titre}"`;

            btnSuivant.textContent = "Niveau Suivant ➡️";

        }



        document.getElementById('victoryMessage').classList.remove('hidden');

        document.getElementById('wordInput').disabled = true;

        document.getElementById('btnSubmit').disabled = true;

        if (isDernierNiveau) {

            document.getElementById('progressBarFill').style.width = '100%';

            document.getElementById('percentIndicator').textContent = '100%';

        } else {

            const progressionPourcent = Math.max(0, Math.min(100, Math.round(((niveauActuelIdx + 1) / BANQUE_NIVEAUX.length) * 100)));

            document.getElementById('progressBarFill').style.width = `${progressionPourcent}%`;

            document.getElementById('percentIndicator').textContent = `${progressionPourcent}%`;

        }

        rendreLeTexte();

        lancerFeuxArtifices(isDernierNiveau);

    }

}



function passerAuNiveauSuivant() {

    niveauActuelIdx++;

    if (niveauActuelIdx >= BANQUE_NIVEAUX.length) {

        niveauActuelIdx = 0;

    }

    sauvegarderNiveau(niveauActuelIdx);

    chargerNiveau();

}



function lancerFeuxArtifices(estDernierNiveau = false) {

    if (typeof confetti !== 'function') {

        return;

    }

    let duree = estDernierNiveau ? 7 * 1000 : 5 * 1000;

    let fin = Date.now() + duree;

    const couleurs = estDernierNiveau ? ['#38bdf8', '#f59e0b', '#ec4899', '#8b5cf6', '#10b981', '#f43f5e'] : ['#38bdf8', '#f59e0b'];


    (function frame() {

        const particleCount = estDernierNiveau ? 18 : 6;

        confetti({

            particleCount,

            angle: 60,

            spread: 80,

            origin: { x: 0, y: 0.6 },

            colors: couleurs,

            scalar: estDernierNiveau ? 1.3 : 1

        });

        confetti({

            particleCount,

            angle: 120,

            spread: 80,

            origin: { x: 1, y: 0.6 },

            colors: couleurs,

            scalar: estDernierNiveau ? 1.3 : 1

        });

        if (Date.now() < fin) { requestAnimationFrame(frame); }

    }());

}



function mettreAJourHistorique() {

    const body = document.getElementById('historyBody');

    body.innerHTML = '';

    historiqueEssais.forEach((essai, index) => {

        const tr = document.createElement('tr');

        tr.className = "hover:bg-slate-50 transition-colors duration-150";



        const colorClass = (essai.occurrences > 0 || essai.occurrences === 'Bonus') ? 'text-emerald-600' : 'text-rose-500';



        tr.innerHTML = `

                    <td class="py-3 px-2 text-slate-400 font-mono">${historiqueEssais.length - index}</td>

                    <td class="py-3 px-2 font-semibold text-slate-700">${essai.mot}</td>

                    <td class="py-3 px-2 text-right font-bold ${colorClass}">${essai.occurrences}</td>

                `;

        body.appendChild(tr);

    });

}



function initialiserJeu() {

    document.getElementById('gameForm').addEventListener('submit', verifierMot);
    document.getElementById('btnHint').addEventListener('click', donnerIndices);
    document.getElementById('btnNextLevel').addEventListener('click', passerAuNiveauSuivant);

    const sauvegardeIdx = lireNiveauSauvegarde();

    if (sauvegardeIdx !== null) {

        const indexSauvegarde = parseInt(sauvegardeIdx, 10);

        if (!Number.isNaN(indexSauvegarde) && indexSauvegarde >= 0 && indexSauvegarde < BANQUE_NIVEAUX.length) {

            niveauActuelIdx = indexSauvegarde;

        }

    }

    chargerNiveau();

}



document.addEventListener('DOMContentLoaded', initialiserJeu);