import { useCallback, useEffect, useState } from 'react';
import { loadLabOrMock, api } from '../api/client';
import type { LabSnapshot } from '../models';
import { useAppState } from '../state/appState';

export function useApi() {
  const { state, dispatch } = useAppState();
  const [refreshing, setRefreshing] = useState(false);

  const refresh = useCallback(async () => {
    setRefreshing(true);
    dispatch({ type: 'SET_LOADING', loading: true });
    const result = await loadLabOrMock();
    dispatch({
      type: 'SET_LAB',
      lab: result.lab,
      fromMock: result.fromMock,
      error: result.error ?? null,
    });
    setRefreshing(false);
    return result;
  }, [dispatch]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
    lab: state.lab as LabSnapshot | null,
    loading: state.loading || refreshing,
    error: state.error,
    fromMock: state.fromMock,
    refresh,
    api,
  };
}
