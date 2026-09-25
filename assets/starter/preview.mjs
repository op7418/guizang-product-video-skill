import {serve} from './server.mjs';
const {url} = await serve(Number(process.env.FILM_PORT || 0));
console.log(url + ' — browser console: await seek(seconds) or playFilm(); preview has no audio.');
