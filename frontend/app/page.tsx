"use client";

import { useEffect, useState, useMemo, useCallback } from "react";

interface Card {
  id: number;
  category: string;
  question: string;
  answer: string;
  hint?: string;
  repetition_count: number;
  interval_days: number;
  ease_factor: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [cards, setCards] = useState<Card[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [onlyDue, setOnlyDue] = useState<boolean>(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [loading, setLoading] = useState(true);
  const [completed, setCompleted] = useState(false);

  const fetchCards = (dueOnly: boolean) => {
    setLoading(true);
    const endpoint = dueOnly
      ? `${API_BASE}/api/cards/due`
      : `${API_BASE}/api/cards/all`;

    fetch(endpoint)
      .then((res) => res.json())
      .then((data: Card[]) => {
        setCards(data);
        setCurrentIndex(0);
        setIsFlipped(false);
        setShowHint(false);
        setCompleted(false);
        setLoading(false);
      })
      .catch((err) => {
        console.error("API error:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchCards(onlyDue);
  }, [onlyDue]);

  const categories = useMemo(() => {
    const set = new Set<string>();
    cards.forEach((c) => set.add(c.category));
    return ["All", ...Array.from(set)];
  }, [cards]);

  const filteredCards = useMemo(() => {
    if (selectedCategory === "All") return cards;
    return cards.filter((c) => c.category === selectedCategory);
  }, [cards, selectedCategory]);

  const handleReview = useCallback(
    async (quality: number) => {
      if (filteredCards.length === 0) return;
      const currentCard = filteredCards[currentIndex];

      try {
        await fetch(`${API_BASE}/api/cards/review`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ card_id: currentCard.id, quality }),
        });
      } catch (err) {
        console.error("Failed to submit review:", err);
      }

      setIsFlipped(false);
      setShowHint(false);

      if (currentIndex + 1 < filteredCards.length) {
        setCurrentIndex((prev) => prev + 1);
      } else {
        setCompleted(true);
      }
    },
    [filteredCards, currentIndex]
  );

  const restartDeck = () => {
    setCurrentIndex(0);
    setIsFlipped(false);
    setShowHint(false);
    setCompleted(false);
  };

  // Keyboard Navigation Listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in an input
      if (["INPUT", "TEXTAREA"].includes((e.target as HTMLElement)?.tagName)) {
        return;
      }

      if (e.code === "Space") {
        e.preventDefault();
        setIsFlipped((prev) => !prev);
      } else if (e.key === "h" || e.key === "H") {
        e.preventDefault();
        setShowHint((prev) => !prev);
      } else if (e.key === "1") {
        e.preventDefault();
        handleReview(1);
      } else if (e.key === "2") {
        e.preventDefault();
        handleReview(3);
      } else if (e.key === "3") {
        e.preventDefault();
        handleReview(4);
      } else if (e.key === "4") {
        e.preventDefault();
        handleReview(5);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleReview]);

  const card = filteredCards[currentIndex];
  const progressPercent =
    filteredCards.length > 0
      ? Math.round((currentIndex / filteredCards.length) * 100)
      : 0;

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col items-center justify-center p-4 sm:p-6">
      {/* Header & Category Controls */}
      <header className="w-full max-w-xl mb-6 flex flex-col items-center">
        <h1 className="text-2xl font-bold tracking-tight text-zinc-100 mb-4">
          TechPrep Spaced Repetition
        </h1>

        {/* Controls Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 w-full mb-4 bg-zinc-900/60 p-2.5 rounded-xl border border-zinc-800 text-xs">
          <button
            onClick={() => setOnlyDue(!onlyDue)}
            className={`px-3 py-1.5 rounded-lg border font-medium transition ${
              onlyDue
                ? "bg-amber-500/20 border-amber-500/40 text-amber-300"
                : "bg-zinc-800 border-zinc-700 text-zinc-400 hover:text-zinc-200"
            }`}
          >
            {onlyDue ? "Showing Due Cards" : "Showing All Cards"}
          </button>

          <div className="flex items-center gap-1.5 overflow-x-auto max-w-[320px]">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => {
                  setSelectedCategory(cat);
                  setCurrentIndex(0);
                  setIsFlipped(false);
                  setShowHint(false);
                  setCompleted(false);
                }}
                className={`px-2.5 py-1 rounded-md text-xs whitespace-nowrap transition ${
                  selectedCategory === cat
                    ? "bg-zinc-100 text-zinc-900 font-semibold"
                    : "text-zinc-400 hover:text-zinc-200 bg-zinc-800/40"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Progress Tracker */}
        {filteredCards.length > 0 && !completed && (
          <div className="w-full">
            <div className="flex justify-between text-[11px] text-zinc-500 uppercase tracking-widest font-mono mb-1.5">
              <span>
                Card {currentIndex + 1} of {filteredCards.length}
              </span>
              <span>{progressPercent}% Complete</span>
            </div>
            <div className="w-full bg-zinc-900 h-1.5 rounded-full overflow-hidden border border-zinc-800">
              <div
                className="bg-emerald-500 h-full transition-all duration-300"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        )}
      </header>

      {/* Main Study Surface */}
      {loading ? (
        <p className="text-zinc-400 animate-pulse text-sm my-16">
          Syncing database schedules...
        </p>
      ) : filteredCards.length === 0 ? (
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 max-w-md text-center my-12">
          <p className="text-zinc-300 font-medium mb-1">No cards to review</p>
          <p className="text-zinc-500 text-xs">
            {onlyDue
              ? "All cards in this set are scheduled for future dates."
              : "No cards found for this category."}
          </p>
        </div>
      ) : completed ? (
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 max-w-md text-center my-8 shadow-2xl">
          <div className="w-12 h-12 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-3 text-lg">
            ✓
          </div>
          <h2 className="text-xl font-bold mb-1">Deck Complete</h2>
          <p className="text-zinc-400 text-xs mb-5">
            Updated intervals have been written to the database via SM-2.
          </p>
          <button
            onClick={restartDeck}
            className="w-full py-2 bg-zinc-100 text-zinc-900 hover:bg-zinc-200 font-semibold rounded-lg text-sm transition"
          >
            Review Set Again
          </button>
        </div>
      ) : (
        <>
          {/* Flip Card Container */}
          <div
            className="w-full max-w-xl h-80 perspective-1000 cursor-pointer select-none"
            onClick={() => setIsFlipped(!isFlipped)}
          >
            <div
              className={`relative w-full h-full duration-500 transform-style-3d ${
                isFlipped ? "rotate-y-180" : ""
              }`}
            >
              {/* Front */}
              <div className="absolute inset-0 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 transition-colors rounded-2xl p-6 sm:p-8 flex flex-col justify-between backface-hidden shadow-xl">
                <div className="flex justify-between items-center">
                  <span className="text-xs uppercase font-bold text-emerald-400 tracking-wider bg-emerald-500/10 px-2.5 py-1 rounded-md border border-emerald-500/20">
                    {card.category}
                  </span>
                  <span className="text-[11px] text-zinc-500 font-mono">
                    [Space] to flip
                  </span>
                </div>

                <p className="text-lg sm:text-xl font-medium text-center text-zinc-100 px-2">
                  {card.question}
                </p>

                <div className="flex justify-between items-end">
                  {card.hint ? (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowHint(!showHint);
                      }}
                      className="text-xs text-zinc-400 hover:text-zinc-200 underline underline-offset-2 flex items-center gap-1"
                    >
                      <span>{showHint ? `Hint: ${card.hint}` : "Show hint"}</span>
                      <kbd className="text-[10px] bg-zinc-800 px-1 py-0.5 rounded border border-zinc-700">H</kbd>
                    </button>
                  ) : (
                    <div />
                  )}
                  <span className="text-[11px] text-zinc-600 font-mono">
                    Reps: {card.repetition_count}
                  </span>
                </div>
              </div>

              {/* Back */}
              <div className="absolute inset-0 bg-zinc-900 border border-zinc-700 rounded-2xl p-6 sm:p-8 flex flex-col justify-between rotate-y-180 backface-hidden shadow-xl">
                <div className="flex justify-between items-center">
                  <span className="text-xs uppercase font-bold text-zinc-400 tracking-wider bg-zinc-800 px-2.5 py-1 rounded-md">
                    Solution
                  </span>
                  <span className="text-[11px] text-zinc-500 font-mono">
                    Interval: {card.interval_days}d
                  </span>
                </div>

                <div className="overflow-y-auto max-h-48 my-auto pr-1">
                  <p className="text-sm sm:text-base text-zinc-200 leading-relaxed whitespace-pre-line text-left">
                    {card.answer}
                  </p>
                </div>

                <div className="text-center text-[11px] text-zinc-500">
                  Rate your recall using keys [1-4] or buttons below
                </div>
              </div>
            </div>
          </div>

          {/* SM-2 Confidence Buttons with Keyboard Badges */}
          <div className="w-full max-w-xl mt-5 grid grid-cols-4 gap-2.5">
            <button
              onClick={() => handleReview(1)}
              className="py-2.5 px-2 bg-red-950/40 hover:bg-red-900/60 border border-red-900/60 text-red-300 rounded-xl text-xs sm:text-sm font-medium transition active:scale-95 flex flex-col items-center"
            >
              <div className="flex items-center gap-1">
                <span>Again</span>
                <kbd className="text-[9px] bg-red-950 px-1 rounded border border-red-800">1</kbd>
              </div>
              <span className="text-[10px] text-red-500/80 mt-0.5">Reset (1d)</span>
            </button>

            <button
              onClick={() => handleReview(3)}
              className="py-2.5 px-2 bg-amber-950/40 hover:bg-amber-900/60 border border-amber-900/60 text-amber-300 rounded-xl text-xs sm:text-sm font-medium transition active:scale-95 flex flex-col items-center"
            >
              <div className="flex items-center gap-1">
                <span>Hard</span>
                <kbd className="text-[9px] bg-amber-950 px-1 rounded border border-amber-800">2</kbd>
              </div>
              <span className="text-[10px] text-amber-500/80 mt-0.5">Moderate</span>
            </button>

            <button
              onClick={() => handleReview(4)}
              className="py-2.5 px-2 bg-blue-950/40 hover:bg-blue-900/60 border border-blue-700/60 text-blue-300 rounded-xl text-xs sm:text-sm font-medium transition active:scale-95 flex flex-col items-center"
            >
              <div className="flex items-center gap-1">
                <span>Good</span>
                <kbd className="text-[9px] bg-blue-950 px-1 rounded border border-blue-800">3</kbd>
              </div>
              <span className="text-[10px] text-blue-500/80 mt-0.5">Standard</span>
            </button>

            <button
              onClick={() => handleReview(5)}
              className="py-2.5 px-2 bg-emerald-950/40 hover:bg-emerald-900/60 border border-emerald-900/60 text-emerald-300 rounded-xl text-xs sm:text-sm font-medium transition active:scale-95 flex flex-col items-center"
            >
              <div className="flex items-center gap-1">
                <span>Easy</span>
                <kbd className="text-[9px] bg-emerald-950 px-1 rounded border border-emerald-800">4</kbd>
              </div>
              <span className="text-[10px] text-emerald-500/80 mt-0.5">Extended</span>
            </button>
          </div>
        </>
      )}
    </main>
  );
}