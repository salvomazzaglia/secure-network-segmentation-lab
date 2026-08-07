import { BANNER_TEXT } from '../models';

export function Banner() {
  return (
    <div className="banner" role="status" aria-live="polite" data-testid="synthetic-banner">
      {BANNER_TEXT}
    </div>
  );
}
