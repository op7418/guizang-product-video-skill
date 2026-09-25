// Static router stub: the film never navigates.
const router = {push() {}, replace() {}, back() {}, forward() {}, refresh() {}, prefetch() {}};
export const useRouter = () => router;
export const usePathname = () => '/chat';
export const useSearchParams = () => new URLSearchParams();
export const useParams = () => ({});
export const redirect = () => {};
export const notFound = () => {};
