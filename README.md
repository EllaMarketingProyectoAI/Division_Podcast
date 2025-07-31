# Dividir Podcast (Railway Ready)

Este servidor Flask divide un video largo (ej. podcast) en clips de 10 minutos y los sube a Supabase.

## JSON de entrada (POST)

```json
{
  "user_id": "usuario123",
  "url_video": "https://<tu-proyecto>.supabase.co/storage/v1/object/public/videospodcast/PodcastCompleto/video.mp4",
  "supabaseFileName": "video.mp4"
}
```

## Deploy

1. Sube a GitHub.
2. Conéctalo a Railway.
3. Agrega variables de entorno desde `.env.example`.
4. ¡Listo!
