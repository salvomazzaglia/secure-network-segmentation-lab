import { VERSION_WARNING, WIRED_DISCLAIMER, WIRELESS_DISCLAIMER } from '../models';

interface Props {
  showWireless?: boolean;
  showWired?: boolean;
}

export function Disclaimers({ showWireless = true, showWired = true }: Props) {
  return (
    <div className="panel" data-testid="disclaimers">
      {showWireless && (
        <p className="disclaimer" data-testid="wireless-disclaimer">
          {WIRELESS_DISCLAIMER}
        </p>
      )}
      {showWired && (
        <p className="disclaimer wired" data-testid="wired-disclaimer">
          {WIRED_DISCLAIMER}
        </p>
      )}
      <p className="disclaimer" data-testid="version-disclaimer">
        {VERSION_WARNING}
      </p>
    </div>
  );
}
