# Related-work additions checked for r17

Accessed 2026-09-29. This is a targeted check of four added references, not a new
audit of the inherited bibliography.

- H. R. Simpson, "Four-slot fully asynchronous communication mechanism,"
  IEE Proceedings E, 137(1), 17-30, 1990, DOI 10.1049/ip-e.1990.0002.
- Hermann Kopetz and Johannes Reisinger, "The non-blocking write protocol NBW:
  A solution to a real-time synchronization problem," IEEE RTSS, 131-137, 1993,
  DOI 10.1109/REAL.1993.393507.
- John Rushby, "Model Checking Simpson's Four-Slot Fully Asynchronous
  Communication Mechanism," SRI CSL technical report, July 3, 2002.
  https://www.csl.sri.com/~rushby/papers/4slot.pdf
- Giorgio Buttazzo, "Why Real-Time Computing?", Automazione e Strumentazione,
  February 2007, 82-88.
  https://retis.santannapisa.it/~giorgio/paps/2007/automazione07.pdf

The SRI primary research report was read for the four-slot analysis and the
two-part NBW comparison (printed pp. 1-3), and its bibliography confirms the
original authors, titles, year, and pages. Direct DOI opens were unavailable;
this report is not a claim to have read the original Simpson or NBW PDFs.
NBW is not described merely as retry-only: its multibuffer variant is retained.
Buttazzo's author-hosted article, pp. 86-87, describes CAB acquire/use/release,
memory duplication, and latest-value semantics.

The manuscript contrasts assigned-frame GPU protection and derived completion
events with these mechanisms. It does not claim that asynchronous buffers
cannot protect readers or that BIM invented basic reader-writer coordination.
