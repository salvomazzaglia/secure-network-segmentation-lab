import { useEffect, useId, useRef } from 'react';
import type { Device, SegmentId } from '../models';
import { APPROVAL_DIALOG_TEXT } from '../models';
import { useAppState } from '../state/appState';

interface Props {
  device: Device | null;
}

export function ApprovalDialog({ device }: Props) {
  const { state, dispatch } = useAppState();
  const titleId = useId();
  const firstRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (state.approvalOpen) firstRef.current?.focus();
  }, [state.approvalOpen]);

  if (!state.approvalOpen || !device) return null;

  const apply = (segment: SegmentId) => {
    dispatch({
      type: 'APPLY_APPROVAL',
      deviceId: device.device_id,
      chosenSegment: segment,
    });
  };

  return (
    <div
      className="dialog-backdrop"
      role="presentation"
      onClick={() => dispatch({ type: 'SET_APPROVAL_OPEN', open: false })}
    >
      <div
        className="dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        data-testid="approval-dialog"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id={titleId}>Synthetic approval</h2>
        <p className="muted">
          Device <strong>{device.alias}</strong> — recommended segment{' '}
          <code>{device.recommended_segment}</code>
        </p>
        <p className="dialog-warning" data-testid="approval-warning">
          {APPROVAL_DIALOG_TEXT}
        </p>
        <div className="toolbar">
          <button
            ref={firstRef}
            type="button"
            className="btn btn-primary"
            onClick={() => apply(device.recommended_segment)}
          >
            Approve recommended
          </button>
          <button type="button" className="btn" onClick={() => apply('quarantine')}>
            Keep quarantined
          </button>
          <button type="button" className="btn" onClick={() => apply('trusted')}>
            Choose Trusted
          </button>
          <button
            type="button"
            className="btn"
            onClick={() => dispatch({ type: 'SET_APPROVAL_OPEN', open: false })}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
