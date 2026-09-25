// Map every plan.json shot id to a view and a builder. Builders receive the master timeline.
import {TitleView, ComponentView, buildTitle, buildComponent} from './sample.jsx';
export const SHOT_VIEWS = {intro: TitleView, component: ComponentView, close: TitleView};
export const SHOT_BUILDERS = {intro: buildTitle('intro'), component: buildComponent('component'), close: buildTitle('close')};
