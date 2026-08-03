# How to Use AI In Trading - Copy This (Free & Easy)

- video_id: hRPBYPO8AhA
- url: https://www.youtube.com/watch?v=hRPBYPO8AhA
- duration: 26:11
- classification: TOOLING

## Summary
This video is a tutorial on using AI tools for trading workflows, not a specific trading strategy. It demonstrates AI applications across six areas: (1) chart analysis and level identification, (2) multi-timeframe analysis consolidation, (3) custom indicator code generation, (4) stock fundamental analysis, (5) trading strategy blind spot review, (6) stock/crypto screening and filtering, and (7) converting indicators into backtestable strategies via Pine Script. The emphasis is on speed, clarity, and reducing manual analysis overhead by delegating pattern recognition and code generation to AI.

## Instruments and timeframes stated
- markets: Stocks, crypto, pound yen (examples), Tesla (backtest example), Apple (fundamental example) [various sections]
- timeframes: Demonstration uses 4-hour, 30-minute, and 5-minute charts; backtesting on 1-hour timeframe [03:00-05:30, 20:00]
- sessions/hours: NOT STATED

## No strategy content

This video contains no original or self-contained trading strategy. Instead, it demonstrates a process for *using AI as a tool* to:

- Read and label chart levels via AI screenshot analysis [00:00-03:00]
- Synthesize multi-timeframe insights into a single directional recommendation [03:00-06:00]
- Generate Pine Script code for custom indicators without manual coding [06:30-09:00]
- Analyze stock fundamentals by uploading financial data or documents to AI [09:00-12:00]
- Debug blind spots in an existing trading strategy by describing entry rules, exit rules, and risk management to AI [12:00-14:00]
- Scan and rank stocks/crypto using Trading View screener data fed to AI for pattern identification [14:00-18:00]
- Convert an existing indicator (Chandelier Exit) into a backtestable Pine Script strategy [18:30-22:00]
- Create a trading journal template with automated calculations [22:30-26:00]

The video illustrates an *AI-assisted workflow*, not a discrete, standalone trading system. No entry rules, stop-loss rules, or take-profit rules are presented as the video's own trading method.

### Example: Chandelier Exit Strategy Conversion

The only concrete strategy example shown is a *conversion* of an existing third-party indicator (Chandelier Exit) into a Pine Script strategy. The speaker does not present this as a novel method; rather, it demonstrates the process of taking existing trading logic and automating it.

**Chandelier Exit Strategy (as AI-generated):**
- Entry: Long when Chandelier Exit shows buy signal; Short when it shows sell signal [19:00-19:30]
- ATR period: 50 [19:30-20:00]
- ATR multiplier: 1 [19:30-20:00]
- Backtest timeframe: 1-hour on Tesla [20:00]
- Backtest result: 60% return, ~4% max drawdown, 1.7 profit factor, 1000+ trades, 25% win rate [20:00-21:30]
- The speaker emphasizes this is a "foundation" and suggests further optimization (trailing stops, trend filters, exit logic adjustments) [21:30-22:30]

This is presented as a proof-of-concept for AI-driven strategy creation, not as a recommended strategy.

---

## Vagueness log

This video does not present a discrete, mechanically-defined trading strategy. Instead, it offers a *meta-process* for using AI to research, code, and refine strategies. Specific gaps:

1. TOOLING: The entire video is a demonstration of AI as an auxiliary tool; no standalone strategy is presented.
2. SUBJECTIVE: Chart analysis output depends entirely on the AI model's interpretation and the prompt given by the user.
3. UNDEFINED-RULE: Multi-timeframe synthesis rules are not defined; AI decides which timeframe takes precedence and how to weight signals.
4. UNDEFINED-RULE: Stock screening criteria are not specified; the user must ask AI for "unusual metrics," "sector rotations," or "undervalued tech stocks," and AI's response is not deterministic without specific filters.
5. SUBJECTIVE: Trading journal review recommendations are based on AI pattern-matching of user notes, which is not mechanically reproducible.

---

## Mechanizability

NOT APPLICABLE — This video is not a trading strategy; it is a workflow guide for using AI as a research and coding assistant. The Chandelier Exit example is mechanically sound (ATR-based trailing stop), but it is not original to the video and is presented only as an example of AI code generation capability.

If forced to rate the *Chandelier Exit example* separately:
- FULL (for the indicator itself, once code is written) — ATR calculation and stop placement are deterministic from OHLCV data.
- However, the video's core message is that AI can *generate* such strategies, not that the user should trade them as-is.

---

## Notable claims and caveats

The speaker frames AI as a solution to speed up analysis ("You don't spend hours analyzing. You grab your screenshot, ask AI, and get a clear map" [02:30]). The video implies that AI can identify "where big money moved" and "key levels" [00:30-01:30], but does not validate whether these AI identifications are accurate or profitable.

For the Chandelier Exit backtest example, the speaker notes:
- "60% return" and "4% max drawdown" sound promising, but he acknowledges this is a "simple strategy" and a "solid foundation" that requires further testing on other timeframes and symbols [21:00-21:30].
- His "biggest concern is whether we could actually stick with this strategy during choppy periods" [21:30], flagging a behavioral risk.
- He emphasizes: "For a strategy that took less than 5 minutes to create, these results are promising" [21:30] — suggesting the backtest is illustrative, not a rigorous evaluation.

Stock and crypto screening recommendations depend on user-defined prompts to AI; there is no systematic ruleset.

No mention is made of transaction costs, spread, slippage, or commission in the Chandelier Exit backtest or any other example.

The video does not explain how to evaluate AI's accuracy or verify its chart-reading claims against actual price levels in the video. AI analysis is presented as gospel truth without validation.
