# backend
Backend amb Python per a un chatbot especialitzat en Minecraft.

## Recuperacio de respostes

El backend utilitza:
- `sentence-transformers` per generar embeddings locals
- recuperacio semantica amb RAG sobre una base documental especialitzada
- reranking i construccio de resposta a partir dels fragments recuperats

## Generacio de construccions

El backend inclou una funcionalitat independent del xat per generar construccions procedurals.

- Endpoint `GET /builds/templates`: retorna les plantilles disponibles
- Endpoint `POST /builds/generate`: rep una plantilla, una mida i un petit prompt opcional
- Sortida: llista de blocs amb coordenades `(x, y, z)` i tipus de bloc
- Els blocs especials tambe poden incloure `state` per ajudar el frontend a renderitzar `stairs`, `slabs`, `fences`, `walls`, `panes`, `doors` i `trapdoors`
- Actualment la plantilla activa principal es `casa_medieval`, que es pot variar amb mida i petits modificadors com `de piedra`, `con jardin`, `dos pisos` o `decorada`

Aquest modul esta pensat per connectar-se a un frontend amb Three.js o `react-three-fiber`, de manera que el navegador pugui renderitzar les estructures com cubs 3D estil Minecraft.
