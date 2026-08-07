import { useEffect } from 'react';
import { createEventsSocket } from '../api/client';
import { useAppState } from '../state/appState';

export function useEvents(enabled = true) {
  const { state, dispatch } = useAppState();

  useEffect(() => {
    if (!enabled) return;
    const ws = createEventsSocket(
      (event) => dispatch({ type: 'PUSH_EVENT', event }),
      (status) => dispatch({ type: 'SET_WS_STATUS', status }),
    );
    return () => {
      ws?.close();
    };
  }, [dispatch, enabled]);

  return {
    events: state.events,
    wsStatus: state.wsStatus,
  };
}
