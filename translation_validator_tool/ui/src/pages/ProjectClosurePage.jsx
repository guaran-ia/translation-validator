import { useEffect, useRef, useState } from 'react';
import { projectAPI } from '../services/api';
import guaraniaLogo from '../images/logo.svg';
import ciditLogo from '../images/logoCidit.svg';
import bidLogo from '../images/bidLogo.webp';

const EMPTY_SUMMARY = {
  stats: { participants: 0, translations: 0, validations: 0, months: 0 },
  timeline: [],
  top_translators: [],
  top_validators: [],
  participants: [],
};

const MEDALS = ['🥇', '🥈', '🥉', '4', '5'];
const TIMELINE_ICONS = ['◇', '1', '2', '✓'];

const safeNumber = (value) => {
  const number = Number(value);
  return Number.isFinite(number) ? number : 0;
};

const formatNumber = (value) => safeNumber(value).toLocaleString('es-PY');

const formatDate = (value) => {
  if (!value) return 'Sin fecha registrada';
  const date = new Date(`${value}T00:00:00`);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('es-PY', { day: '2-digit', month: 'short', year: 'numeric' }).format(date);
};

const initialsFor = (name) => {
  const parts = (name || 'Participante').trim().split(/\s+/).filter(Boolean);
  return parts.slice(0, 2).map((part) => part[0]?.toUpperCase()).join('') || 'P';
};

const useReducedMotion = () => {
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const update = () => setReducedMotion(mediaQuery.matches);
    update();
    mediaQuery.addEventListener('change', update);
    return () => mediaQuery.removeEventListener('change', update);
  }, []);

  return reducedMotion;
};

const useInViewOnce = (options = {}) => {
  const ref = useRef(null);
  const reducedMotion = useReducedMotion();
  const [inView, setInView] = useState(reducedMotion);

  useEffect(() => {
    if (reducedMotion) {
      setInView(true);
      return undefined;
    }

    const element = ref.current;
    if (!element || inView) return undefined;

    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setInView(true);
        observer.disconnect();
      }
    }, { threshold: 0.25, rootMargin: '0px 0px -8% 0px', ...options });

    observer.observe(element);
    return () => observer.disconnect();
  }, [inView, options, reducedMotion]);

  return [ref, inView, reducedMotion];
};

const SectionReveal = ({ children, className = '', delay = 0, ...props }) => {
  const [ref, inView, reducedMotion] = useInViewOnce();

  return (
    <section
      ref={ref}
      className={`${className} transition-all duration-700 ease-out ${inView ? 'translate-y-0 opacity-100' : 'translate-y-6 opacity-0'}`}
      style={{ transitionDelay: reducedMotion ? '0ms' : `${delay}ms` }}
      {...props}
    >
      {children}
    </section>
  );
};

const AnimatedNumber = ({ value, start, duration = 1600 }) => {
  const reducedMotion = useReducedMotion();
  const target = safeNumber(value);
  const [displayValue, setDisplayValue] = useState(reducedMotion || start ? target : 0);
  const hasAnimatedRef = useRef(false);

  useEffect(() => {
    if (!start) return undefined;

    if (reducedMotion || target === 0) {
      setDisplayValue(target);
      hasAnimatedRef.current = true;
      return undefined;
    }

    if (hasAnimatedRef.current) return undefined;
    hasAnimatedRef.current = true;

    const startTime = performance.now();
    let frameId;

    const tick = (now) => {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const nextValue = progress === 1 ? target : Math.round(target * eased);
      setDisplayValue(nextValue);

      if (progress < 1) frameId = requestAnimationFrame(tick);
    };

    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, [duration, reducedMotion, start, target]);

  return <>{formatNumber(displayValue)}</>;
};

const MetricIcon = ({ type }) => {
  const paths = {
    people: 'M17 20v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2 M9 10a4 4 0 1 0 0-8 4 4 0 0 0 0 8 M23 20v-2a4 4 0 0 0-3-3.87 M16 3.13a4 4 0 0 1 0 7.75',
    translations: 'M4 5h10 M4 9h7 M5 19l4-4H6a4 4 0 0 1-4-4V5a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v2 M15 13h5 M15 17h3 M19 23l-4-4h3a4 4 0 0 0 4-4v-2a4 4 0 0 0-4-4h-4a4 4 0 0 0-4 4v2',
    validations: 'M20 6 9 17l-5-5 M4 21h16a2 2 0 0 0 2-2V5',
    months: 'M7 2v4 M17 2v4 M3 10h18 M5 4h14a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2',
  };

  return (
    <svg className="h-7 w-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={paths[type]} />
    </svg>
  );
};

const LoadingSkeleton = () => (
  <div className="min-h-screen bg-gradient-to-br from-slate-950 via-teal-950 to-slate-900 px-4 py-8">
    <div className="mx-auto max-w-6xl animate-pulse space-y-8">
      <div className="h-14 w-44 rounded-xl bg-white/15" />
      <div className="rounded-3xl border border-white/10 bg-white/10 p-8">
        <div className="h-12 w-56 rounded bg-white/15" />
        <div className="mt-6 h-4 max-w-3xl rounded bg-white/10" />
        <div className="mt-3 h-4 max-w-2xl rounded bg-white/10" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[0, 1, 2, 3].map((item) => <div key={item} className="h-36 rounded-2xl bg-white/10" />)}
      </div>
    </div>
  </div>
);

const StatCard = ({ label, value, prefix = '', icon, start, delay = 0 }) => (
  <div
    className="closure-stat-card group relative overflow-hidden rounded-3xl border border-teal-100/20 bg-white/[0.94] p-5 shadow-xl shadow-slate-950/10 transition duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-teal-950/20"
    style={{ transitionDelay: `${delay}ms` }}
  >
    <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-teal-300 via-cyan-300 to-teal-500" />
    <div className="absolute -right-10 -top-10 h-28 w-28 rounded-full bg-teal-300/20 blur-2xl transition duration-300 group-hover:bg-teal-300/30" />
    <div className="relative flex items-start justify-between gap-4">
      <div>
        <p className="closure-stat-number text-4xl font-black tracking-tight text-slate-950 sm:text-5xl">
          {prefix}<AnimatedNumber value={value} start={start} />
        </p>
        <p className="closure-stat-label mt-3 text-sm font-black uppercase tracking-wide text-teal-800">{label}</p>
      </div>
      <div className="closure-stat-icon rounded-2xl border border-teal-100 bg-teal-50 p-3 text-teal-700 shadow-sm">
        <MetricIcon type={icon} />
      </div>
    </div>
  </div>
);

const MetricsSection = ({ stats, hasActivity }) => {
  const [ref, inView] = useInViewOnce({ threshold: 0.2 });

  return (
    <section ref={ref} className="closure-metrics-section mt-24 sm:mt-32" aria-labelledby="achievements-title">
      <div className="max-w-2xl">
        <p className="text-sm font-black uppercase tracking-[0.25em] text-teal-200">Resultados finales</p>
        <h2 id="achievements-title" className="mt-2 text-3xl font-black text-white sm:text-4xl">Lo que logramos juntos</h2>
      </div>
      {!hasActivity && <p className="mt-5 rounded-2xl bg-white/10 p-4 text-teal-50">Todavía no existen traducciones, validaciones o participantes registrados en el resumen.</p>}
      <div className="closure-metrics-grid mt-7 grid grid-cols-1 gap-4 min-[380px]:grid-cols-2 lg:grid-cols-4">
        <StatCard prefix="+" value={stats.participants} label="personas participaron" icon="people" start={inView} delay={0} />
        <StatCard value={stats.translations} label="traducciones realizadas" icon="translations" start={inView} delay={80} />
        <StatCard value={stats.validations} label="validaciones completadas" icon="validations" start={inView} delay={160} />
        <StatCard value={stats.months} label="meses de trabajo" icon="months" start={inView} delay={240} />
      </div>
    </section>
  );
};

const TimelineSection = ({ timeline }) => {
  const [ref, inView, reducedMotion] = useInViewOnce({ threshold: 0.25 });

  return (
    <section ref={ref} className="closure-timeline-section mt-16 sm:mt-24" aria-labelledby="timeline-title">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-black uppercase tracking-[0.25em] text-teal-200">Recorrido</p>
          <h2 id="timeline-title" className="mt-2 text-3xl font-black text-white sm:text-4xl">Línea de tiempo</h2>
        </div>
      </div>

      <div className="relative mt-10 hidden px-6 md:block">
        <div className="absolute left-10 right-10 top-[4.95rem] h-px bg-white/15" />
        <div
          className="absolute left-10 right-10 top-[4.95rem] h-px origin-left bg-gradient-to-r from-teal-300 via-cyan-200 to-teal-400 transition-transform duration-[1300ms] ease-out"
          style={{ transform: inView || reducedMotion ? 'scaleX(1)' : 'scaleX(0)' }}
        />
        <div className="grid grid-cols-4 gap-6">
          {timeline.map((item, index) => {
            const isEdge = index === 0 || index === timeline.length - 1;
            const isLast = index === timeline.length - 1;
            return (
              <div
                key={`${item.label}-${index}`}
                className={`relative flex flex-col items-center text-center transition-all duration-500 ease-out ${inView || reducedMotion ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'}`}
                style={{ transitionDelay: reducedMotion ? '0ms' : `${450 + index * 160}ms` }}
              >
                <p className="mb-7 min-h-[2.5rem] text-sm font-black uppercase tracking-wide text-white">{item.label}</p>
                <div className={`relative z-10 flex h-14 w-14 items-center justify-center rounded-full border text-lg font-black shadow-xl ${isLast ? 'border-teal-200 bg-teal-300 text-slate-950 shadow-teal-950/30' : isEdge ? 'border-teal-200/70 bg-slate-950 text-teal-100' : 'border-teal-300/50 bg-teal-950 text-teal-100'}`}>
                  {TIMELINE_ICONS[index] || index + 1}
                </div>
                <p className="mt-5 text-sm font-semibold text-teal-100">{formatDate(item.date)}</p>
              </div>
            );
          })}
        </div>
      </div>

      <div className="closure-timeline-mobile relative mt-8 md:hidden">
        <div className="closure-timeline-mobile-line absolute bottom-8 left-7 top-5 w-px bg-white/15" />
        <div
          className="closure-timeline-mobile-progress absolute bottom-8 left-7 top-5 w-px origin-top bg-gradient-to-b from-teal-300 via-cyan-200 to-teal-400 transition-transform duration-[1300ms] ease-out"
          style={{ transform: inView || reducedMotion ? 'scaleY(1)' : 'scaleY(0)' }}
        />
        <div className="closure-timeline-mobile-list space-y-7">
          {timeline.map((item, index) => {
            const isLast = index === timeline.length - 1;
            return (
              <div
                key={`${item.label}-mobile-${index}`}
                className={`closure-timeline-mobile-item relative grid grid-cols-[3.5rem_1fr] gap-4 transition-all duration-500 ease-out ${inView || reducedMotion ? 'translate-x-0 opacity-100' : 'translate-x-4 opacity-0'}`}
                style={{ transitionDelay: reducedMotion ? '0ms' : `${380 + index * 140}ms` }}
              >
                <div className={`closure-timeline-mobile-node relative z-10 flex h-14 w-14 items-center justify-center rounded-full border text-base font-black shadow-lg ${isLast ? 'border-teal-200 bg-teal-300 text-slate-950' : 'border-teal-300/50 bg-slate-950 text-teal-100'}`}>
                  {TIMELINE_ICONS[index] || index + 1}
                </div>
                <div className="closure-timeline-mobile-content pb-2">
                  <h3 className="closure-timeline-mobile-title text-lg font-black text-white">{item.label}</h3>
                  <p className="closure-timeline-mobile-date mt-1 text-sm font-semibold text-teal-100">{formatDate(item.date)}</p>

                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

const RankingList = ({ title, items, countLabel }) => {
  const [ref, inView, reducedMotion] = useInViewOnce({ threshold: 0.2 });

  return (
    <section ref={ref} className="closure-ranking-card rounded-3xl border border-white/10 bg-white/[0.94] p-5 shadow-xl shadow-slate-950/10 sm:p-6">
      <h3 className="closure-ranking-title text-xl font-black text-slate-950">{title}</h3>
      {items.length === 0 ? (
        <p className="mt-5 rounded-xl bg-slate-50 p-4 text-sm text-slate-600">Todavía no hay datos registrados.</p>
      ) : (
        <ol className="closure-ranking-list mt-5 space-y-3">
          {items.slice(0, 5).map((item, index) => {
            const isPodium = index < 3;
            return (
              <li
                key={`${item.name}-${index}`}
                className={`closure-ranking-row group grid grid-cols-[auto_1fr_auto] items-center gap-3 rounded-2xl border px-3 py-3 transition duration-300 hover:-translate-y-0.5 ${isPodium ? 'border-teal-100 bg-gradient-to-r from-slate-50 to-teal-50/60' : 'border-slate-100 bg-slate-50'}`}
                style={{
                  opacity: inView || reducedMotion ? 1 : 0,
                  transform: inView || reducedMotion ? 'translateY(0)' : 'translateY(12px)',
                  transitionDelay: reducedMotion ? '0ms' : `${index * 110}ms`,
                }}
              >
                <span className={`closure-ranking-medal flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-black shadow-sm ${index === 0 ? 'bg-amber-100 text-amber-800' : index === 1 ? 'bg-slate-200 text-slate-700' : index === 2 ? 'bg-orange-100 text-orange-800' : 'bg-teal-50 text-teal-800'}`}>
                  {MEDALS[index]}
                </span>
                <div className="closure-ranking-person min-w-0">
                  <div className="flex min-w-0 items-center gap-2">
                    <span className="closure-ranking-avatar flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-900 text-xs font-black text-teal-100">{initialsFor(item.name)}</span>
                    <p className="closure-ranking-name truncate text-sm font-black text-slate-900 sm:text-base">{item.name || 'Participante'}</p>
                  </div>
                </div>
                <div className="closure-ranking-count text-right">
                  <p className="closure-ranking-count-number text-lg font-black text-teal-800">{formatNumber(item.count)}</p>
                  <p className="closure-ranking-count-label text-[11px] font-bold uppercase tracking-wide text-slate-500">{countLabel}</p>
                </div>
              </li>
            );
          })}
        </ol>
      )}
    </section>
  );
};

const ParticipantsModal = ({ participants, onClose }) => {
  const [query, setQuery] = useState('');
  const closeButtonRef = useRef(null);
  const dialogRef = useRef(null);

  useEffect(() => {
    const previousActiveElement = document.activeElement;
    closeButtonRef.current?.focus();

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') onClose();

      if (event.key === 'Tab' && dialogRef.current) {
        const focusableElements = dialogRef.current.querySelectorAll('button, input, [href], [tabindex]:not([tabindex="-1"])');
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (event.shiftKey && document.activeElement === firstElement) {
          event.preventDefault();
          lastElement?.focus();
        } else if (!event.shiftKey && document.activeElement === lastElement) {
          event.preventDefault();
          firstElement?.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      previousActiveElement?.focus?.();
    };
  }, [onClose]);

  const normalizedQuery = query.trim().toLowerCase();
  const visibleParticipants = participants.filter((participant) =>
    (participant.name || '').toLowerCase().includes(normalizedQuery)
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/75 px-4 py-6" onMouseDown={onClose}>
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="participants-title"
        className="max-h-[90vh] w-full max-w-3xl overflow-hidden rounded-3xl bg-white shadow-2xl"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 border-b border-slate-200 p-5">
          <div>
            <h2 id="participants-title" className="text-xl font-black text-slate-900">Personas participantes</h2>
            <p className="mt-1 text-sm text-slate-600">Ordenadas por contribuciones totales. No se muestran emails.</p>
          </div>
          <button
            ref={closeButtonRef}
            type="button"
            onClick={onClose}
            className="rounded-full bg-slate-100 px-4 py-2 text-sm font-bold text-slate-700 transition hover:bg-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
          >
            Cerrar
          </button>
        </div>

        <div className="p-5">
          <label htmlFor="participant-search" className="block text-sm font-bold text-slate-700">Buscar por nombre</label>
          <input
            id="participant-search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-base text-slate-900 placeholder-slate-400 outline-none transition focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
            placeholder="Escribí un nombre"
          />
        </div>

        <div className="max-h-[52vh] overflow-y-auto px-5 pb-5">
          {visibleParticipants.length === 0 ? (
            <p className="rounded-xl bg-slate-50 p-4 text-sm text-slate-600">No se encontraron participantes.</p>
          ) : (
            <div className="divide-y divide-slate-100 overflow-hidden rounded-2xl border border-slate-200">
              {visibleParticipants.map((participant, index) => (
                <div key={`${participant.name}-${index}`} className="grid gap-2 px-4 py-3 sm:grid-cols-[1fr_auto_auto_auto] sm:items-center">
                  <p className="min-w-0 truncate font-bold text-slate-900">{participant.name || 'Participante'}</p>
                  <p className="text-sm text-slate-600">{formatNumber(participant.translations)} traducciones</p>
                  <p className="text-sm text-slate-600">{formatNumber(participant.validations)} validaciones</p>
                  <p className="text-sm font-black text-teal-800">{formatNumber(participant.total)} total</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const ProjectClosurePage = () => {
  const [summary, setSummary] = useState(EMPTY_SUMMARY);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showParticipants, setShowParticipants] = useState(false);

  const loadSummary = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await projectAPI.getSummary();
      setSummary({ ...EMPTY_SUMMARY, ...response.data });
    } catch (err) {
      console.error('Error cargando resumen del proyecto:', err);
      setError('No pudimos cargar el resumen final del proyecto. Intentá nuevamente en unos minutos.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummary();
  }, []);

  if (loading) return <LoadingSkeleton />;

  const stats = { ...EMPTY_SUMMARY.stats, ...(summary.stats || {}) };
  const timeline = summary.timeline || [];
  const participants = summary.participants || [];
  const hasActivity = safeNumber(stats.translations) > 0 || safeNumber(stats.validations) > 0 || safeNumber(stats.participants) > 0;

  return (
    <main className="min-h-screen overflow-x-hidden bg-gradient-to-br from-slate-950 via-teal-950 to-slate-900 text-white">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-32 -top-32 h-80 w-80 rounded-full bg-teal-500/20 blur-3xl" />
        <div className="absolute -bottom-40 right-0 h-96 w-96 rounded-full bg-emerald-300/10 blur-3xl" />
        <div className="absolute left-1/2 top-1/3 h-72 w-72 -translate-x-1/2 rounded-full bg-cyan-300/5 blur-3xl" />
      </div>

      <div className="closure-page-container relative mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
        <header className="closure-header flex flex-wrap items-center justify-between gap-4 py-4">
          <img src={guaraniaLogo} alt="Mbo'ehara Digital" className="closure-header-logo h-12 w-auto" />
        </header>

        {error ? (
          <section className="mt-12 rounded-3xl border border-red-200/30 bg-white p-8 text-center text-slate-900 shadow-2xl">
            <h1 className="text-3xl font-black">No pudimos cargar el resumen</h1>
            <p className="mx-auto mt-3 max-w-xl text-slate-600">{error}</p>
            <button type="button" onClick={loadSummary} className="mt-6 rounded-full bg-teal-600 px-6 py-3 font-bold text-white transition hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2">
              Reintentar
            </button>
          </section>
        ) : (
          <>
            <section className="closure-hero relative mt-8 overflow-hidden rounded-[2rem] border border-white/10 bg-white/10 p-6 shadow-2xl shadow-slate-950/20 backdrop-blur motion-safe:animate-[fadeIn_700ms_ease-out_1_both] sm:p-10">
              <div className="absolute -left-16 top-8 h-40 w-40 rounded-full bg-teal-300/10 blur-3xl" />
              <div className="relative max-w-4xl">
                <h1 className="closure-hero-title relative mt-4 text-5xl font-black leading-none text-white motion-safe:animate-[fadeInUp_700ms_ease-out_140ms_both] sm:text-7xl">
                  <span className="absolute -inset-x-4 bottom-0 top-5 -z-10 rounded-full bg-teal-300/10 blur-2xl" />
                  ¡Aguyje!
                </h1>
                <div className="closure-hero-copy mt-6 space-y-5 text-lg leading-8 text-teal-50 sm:text-xl">
                  <p className="font-bold text-white motion-safe:animate-[fadeInUp_700ms_ease-out_220ms_both]">Gracias por ser parte de este proyecto.</p>
                  <p className="motion-safe:animate-[fadeInUp_700ms_ease-out_300ms_both]">Durante estos meses construimos juntos un recurso que busca aportar al fortalecimiento y la preservación del idioma guaraní.</p>
                  <p className="motion-safe:animate-[fadeInUp_700ms_ease-out_380ms_both]">Cada traducción, cada validación y cada minuto dedicado fue posible gracias al compromiso de una comunidad que decidió aportar su conocimiento.</p>
                  <p className="closure-hero-highlight border-l-4 border-teal-300 pl-5 text-2xl font-black leading-tight text-white motion-safe:animate-[fadeInUp_700ms_ease-out_460ms_both]">La actividad ha finalizado, pero todo lo construido queda como resultado del esfuerzo de todos.</p>
                </div>
              </div>
            </section>

            <MetricsSection stats={stats} hasActivity={hasActivity} />
            <TimelineSection timeline={timeline} />

            <SectionReveal className="closure-featured-section mt-16 sm:mt-24" aria-labelledby="featured-title">
              <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
                <div className="max-w-2xl">
                  <p className="text-sm font-black uppercase tracking-[0.25em] text-teal-200">Reconocimiento</p>
                  <h2 id="featured-title" className="mt-2 text-3xl font-black text-white sm:text-4xl">Personas destacadas</h2>
                  <p className="mt-2 text-sm leading-6 text-teal-100">Una mención compacta a quienes más aportaron en cada etapa, sin perder el foco comunitario del cierre.</p>
                </div>
              </div>
              <div className="closure-ranking-grid mt-7 grid gap-4 lg:grid-cols-2">
                <RankingList title="Traductores destacados" items={summary.top_translators || []} countLabel="traducciones" />
                <RankingList title="Validadores destacados" items={summary.top_validators || []} countLabel="validaciones" />
              </div>
              <div className="closure-participants-action mt-6 flex justify-center sm:justify-end">
                <button type="button" onClick={() => setShowParticipants(true)} className="closure-participants-button rounded-full border border-emerald-300/60 bg-emerald-500 px-5 py-3 text-sm font-black text-slate-950 shadow-lg shadow-emerald-950/20 transition hover:-translate-y-0.5 hover:bg-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-200">
                  Ver todas las personas que hicieron posible la actividad →
                </button>
              </div>
            </SectionReveal>

            <SectionReveal className="closure-final-message relative mt-16 overflow-hidden rounded-[2rem] border border-teal-200/15 bg-white/[0.07] p-6 shadow-2xl shadow-slate-950/10 sm:mt-24 sm:p-10" aria-labelledby="human-closing-title">
              <div className="absolute right-6 top-6 hidden h-28 w-48 opacity-25 sm:block" aria-hidden="true">
                <svg viewBox="0 0 220 120" className="h-full w-full text-teal-200" fill="none">
                  <path d="M20 90 C55 20, 95 110, 130 45 S190 35, 205 85" stroke="currentColor" strokeWidth="1" />
                  {[20, 65, 112, 158, 205].map((cx, index) => <circle key={cx} cx={cx} cy={[90, 50, 74, 38, 85][index]} r="4" fill="currentColor" />)}
                </svg>
              </div>
              <div className="relative max-w-3xl">
                <p className="closure-final-kicker text-sm font-black uppercase tracking-[0.25em] text-teal-200">Permanencia</p>
                <h2 id="human-closing-title" className="closure-final-title mt-3 text-3xl font-black text-white sm:text-4xl">Este resultado también lleva tu aporte.</h2>
                <p className="closure-final-copy mt-5 text-lg leading-8 text-teal-50">Cada palabra traducida y cada validación realizada ayudaron a construir un recurso que busca fortalecer la presencia del guaraní en la tecnología. Gracias por compartir tu tiempo, tu conocimiento y tu compromiso con nuestra lengua.</p>
                <p className="closure-final-highlight mt-6 border-l-4 border-teal-300 pl-5 text-2xl font-black leading-tight text-white">Lo construido queda. El aporte de esta comunidad también.</p>
              </div>
            </SectionReveal>

            <footer className="closure-footer mt-16 border-t border-white/10 py-10 sm:mt-24" aria-label="Instituciones">
              <p className="closure-footer-text text-center text-xs font-bold uppercase tracking-[0.25em] text-teal-100/80">Un proyecto desarrollado con el acompañamiento de:</p>
              <div className="closure-footer-logos mt-7 flex flex-col items-center justify-center gap-8 sm:flex-row sm:gap-12">
                <img src={guaraniaLogo} alt="Mbo'ehara Digital" className="closure-footer-logo h-12 w-auto max-w-[210px]" />
                <img src={ciditLogo} alt="CIDIT" className="closure-footer-logo h-12 w-auto max-w-[210px]" />
                <img src={bidLogo} alt="BID" className="closure-footer-logo h-12 w-auto max-w-[210px]" />
              </div>
            </footer>
          </>
        )}
      </div>

      <style>{`
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
        @media (max-width: 640px) {
          .closure-page-container {
            width: 100%;
            max-width: 100%;
            padding-left: 20px;
            padding-right: 20px;
            padding-top: 16px;
            padding-bottom: 28px;
          }

          .closure-header {
            padding-top: 8px;
            padding-bottom: 10px;
          }

          .closure-header-logo {
            height: 2.45rem;
          }

          .closure-hero {
            margin-top: 14px;
            border-radius: 1.45rem;
            padding: 30px 24px;
          }

          .closure-hero-title {
            margin-top: 0;
            font-size: clamp(2.3rem, 11vw, 3.2rem);
          }

          .closure-hero-copy {
            margin-top: 18px;
            gap: 14px;
            font-size: 1rem;
            line-height: 1.58;
          }

          .closure-hero-highlight,
          .closure-final-highlight {
            padding-left: 14px;
            font-size: 1.18rem;
            line-height: 1.28;
          }

          .closure-metrics-section,
          .closure-timeline-section,
          .closure-featured-section,
          .closure-final-message {
            margin-top: 72px;
          }

          .closure-metrics-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
            margin-top: 20px;
          }

          .closure-stat-card {
            min-width: 0;
            border-radius: 1.15rem;
            padding: 16px 12px 14px;
          }

          .closure-stat-card > .relative {
            gap: 8px;
          }

          .closure-stat-number {
            min-height: 2.45rem;
            font-size: clamp(1.75rem, 8.6vw, 2.45rem);
            line-height: 1;
            font-variant-numeric: tabular-nums;
            white-space: nowrap;
          }

          .closure-stat-label {
            margin-top: 9px;
            overflow-wrap: anywhere;
            font-size: 0.68rem;
            line-height: 1.22;
            letter-spacing: 0.04em;
          }

          .closure-stat-icon {
            border-radius: 0.95rem;
            padding: 8px;
          }

          .closure-stat-icon svg {
            height: 1.2rem;
            width: 1.2rem;
          }

          .closure-timeline-mobile {
            width: fit-content;
            max-width: 100%;
            margin-top: 26px;
            margin-inline: auto;
          }

          .closure-timeline-mobile-line,
          .closure-timeline-mobile-progress {
            left: 1.5rem;
            top: 1.5rem;
            bottom: 1.5rem;
          }

          .closure-timeline-mobile-list {
            display: flex;
            flex-direction: column;
            gap: 22px;
          }

          .closure-timeline-mobile-item {
            grid-template-columns: 3rem minmax(0, 1fr);
            gap: 12px;
            align-items: start;
            width: min(100%, 18rem);
          }

          .closure-timeline-mobile-node {
            height: 3rem;
            width: 3rem;
            font-size: 0.92rem;
          }

          .closure-timeline-mobile-content {
            min-width: 0;
            padding-bottom: 0;
            padding-top: 1px;
          }

          .closure-timeline-mobile-title {
            font-size: 1rem;
            line-height: 1.25;
          }

          .closure-timeline-mobile-date {
            margin-top: 3px;
            font-size: 0.82rem;
            line-height: 1.3;
          }

          .closure-timeline-mobile-status {
            margin-top: 7px;
            padding: 3px 10px;
            font-size: 0.68rem;
          }

          .closure-ranking-grid {
            margin-top: 22px;
            gap: 14px;
          }

          .closure-ranking-card {
            width: 100%;
            min-width: 0;
            border-radius: 1.35rem;
            padding: 16px;
          }

          .closure-ranking-title {
            font-size: 1.05rem;
          }

          .closure-ranking-list {
            margin-top: 14px;
            display: flex;
            flex-direction: column;
            gap: 9px;
          }

          .closure-ranking-row {
            grid-template-columns: auto minmax(0, 1fr) minmax(4.35rem, auto);
            gap: 8px;
            border-radius: 1rem;
            padding: 10px;
          }

          .closure-ranking-medal {
            height: 2rem;
            width: 2rem;
            font-size: 0.78rem;
          }

          .closure-ranking-person,
          .closure-ranking-name {
            min-width: 0;
          }

          .closure-ranking-avatar {
            height: 1.75rem;
            width: 1.75rem;
            font-size: 0.62rem;
          }

          .closure-ranking-name {
            font-size: 0.86rem;
            line-height: 1.15;
          }

          .closure-ranking-count {
            min-width: 4.35rem;
          }

          .closure-ranking-count-number {
            font-size: 1rem;
            line-height: 1.05;
            font-variant-numeric: tabular-nums;
          }

          .closure-ranking-count-label {
            margin-top: 2px;
            font-size: 0.54rem;
            letter-spacing: 0.035em;
          }

          .closure-participants-action {
            margin-top: 18px;
          }

          .closure-participants-button {
            display: inline-flex;
            min-height: 48px;
            width: 100%;
            align-items: center;
            justify-content: center;
            padding: 11px 14px;
            text-align: center;
            font-size: 0.78rem;
            line-height: 1.2;
          }

          .closure-participants-button:active {
            transform: scale(0.985);
            opacity: 0.92;
          }

          .closure-final-message {
            border-radius: 1.45rem;
            padding: 24px 20px;
          }

          .closure-final-kicker {
            font-size: 0.7rem;
            letter-spacing: 0.18em;
          }

          .closure-final-title {
            margin-top: 10px;
            font-size: clamp(1.55rem, 7vw, 2rem);
            line-height: 1.08;
          }

          .closure-final-copy {
            margin-top: 16px;
            font-size: 0.98rem;
            line-height: 1.58;
          }

          .closure-final-highlight {
            margin-top: 18px;
          }

          .closure-footer {
            margin-top: 56px;
            padding-top: 28px;
            padding-bottom: 28px;
          }

          .closure-footer-text {
            margin-left: auto;
            margin-right: auto;
            max-width: 18rem;
            font-size: 0.68rem;
            line-height: 1.45;
            letter-spacing: 0.1em;
          }

          .closure-footer-logos {
            margin-top: 22px;
            gap: 22px;
          }

          .closure-footer-logo {
            height: auto;
            max-height: 2.35rem;
            max-width: 10.5rem;
          }
        }

        @media (max-width: 340px) {
          .closure-page-container {
            padding-left: 16px;
            padding-right: 16px;
          }

          .closure-stat-card {
            padding-left: 10px;
            padding-right: 10px;
          }

          .closure-stat-icon {
            padding: 6px;
          }

          .closure-ranking-row {
            gap: 7px;
            padding-left: 8px;
            padding-right: 8px;
          }

          .closure-ranking-avatar {
            display: none;
          }

          .closure-participants-button {
            font-size: 0.74rem;
          }
        }

        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
          }
        }
      `}</style>

      {showParticipants && <ParticipantsModal participants={participants} onClose={() => setShowParticipants(false)} />}
    </main>
  );
};

export default ProjectClosurePage;
