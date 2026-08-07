import { useEffect, useState } from 'react';
import { useAppState } from '../state/appState';

export function useReducedMotion(): boolean {
  const { dispatch } = useAppState();
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return;
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const apply = () => {
      setReduced(mq.matches);
      dispatch({ type: 'SET_REDUCED_MOTION', value: mq.matches });
    };
    apply();
    mq.addEventListener('change', apply);
    return () => mq.removeEventListener('change', apply);
  }, [dispatch]);

  return reduced;
}
