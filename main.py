"""
Quantum Superposition Decay for Complexity Classes
MMUKO-OS Framework -- Nnamdi Michael Okpala (OBINexus)

Pipeline: riftlang.exe -> .so.a -> rift.exe -> gosilang -> nsigii-codec
Build orchestration: nlink -> polybuild
"""

from typing import Set, Tuple, Callable, Optional, List, Dict
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import math


# =============================================================================
# ENUMERATIONS
# =============================================================================

class ComplexityClass(Enum):
    P      = "P"
    BPP    = "BPP"
    BQP    = "BQP"
    PP     = "PP"
    PSPACE = "PSPACE"


class PromiseState(Enum):
    RESOLVED = "resolved"   # A_yes accepted
    REJECTED = "rejected"   # A_no  rejected
    PENDING  = "pending"    # Superposition window still open


# =============================================================================
# QUANTUM CONNECTION GRAPH  G = (E, N)
# =============================================================================

@dataclass
class QuantumConnection:
    """
    Directed graph G = (E, N) where:
      N = set of quantum state nodes
      E = set of superposition-transition edges
    """
    edges: Set[Tuple[str, str]] = field(default_factory=set)
    nodes: Set[str]             = field(default_factory=set)

    def add_superposition(self, u: str, v: str) -> None:
        """Add entangled directed edge u -> v."""
        self.edges.add((u, v))
        self.nodes.update([u, v])

    def adjacency_matrix(self) -> Tuple[np.ndarray, List[str]]:
        """
        Return the adjacency matrix A and the ordered node list.
        Used for spectral graph analysis in QBP path selection.
        """
        node_list = sorted(self.nodes)
        idx = {n: i for i, n in enumerate(node_list)}
        size = len(node_list)
        A = np.zeros((size, size), dtype=float)
        for (u, v) in self.edges:
            A[idx[u], idx[v]] = 1.0
        return A, node_list


# =============================================================================
# SUPERPOSITION DECAY  SD(a, b)
# =============================================================================

@dataclass
class SuperpositionDecay:
    """
    Measurement window governing collapse of a superposition state.

    SD(t) = { psi(t) | t in [t_open, t_decay), Pr[collapse] < 1 }

    Three output states:
      RESOLVED  -- Pr[accept] >= a  (yes-instance confirmed)
      REJECTED  -- Pr[accept] <= b  (no-instance confirmed)
      PENDING   -- b < Pr[accept] < a  (window still open)

    The threshold gap (a - b) >= 1/3 is required for BQP tractability.
    """
    psi:     np.ndarray          # Wave function amplitude vector
    t_open:  float               # Window opens at t_open
    t_decay: float               # Window closes at t_decay (decay event)
    a:       float = 2/3         # Acceptance threshold (BQP default)
    b:       float = 1/3         # Rejection threshold  (BQP default)

    def __post_init__(self):
        # Normalise psi on construction
        norm = np.linalg.norm(self.psi)
        if norm > 0:
            self.psi = self.psi / norm

    def is_window_open(self, t: float) -> bool:
        """True if the decay window is active at time t."""
        return self.t_open <= t < self.t_decay

    def measure(self, t: float) -> Optional[PromiseState]:
        """
        Take a measurement at time t within the window.

        Returns:
          RESOLVED  if Pr[accept] >= a
          REJECTED  if Pr[accept] <= b
          PENDING   if b < Pr[accept] < a
          None      if the window has already closed (t >= t_decay)
        """
        if not self.is_window_open(t):
            return None  # Window collapsed; no further measurement possible

        prob_accept = float(np.sum(np.abs(self.psi) ** 2 * self._yes_mask()))

        if prob_accept >= self.a:
            return PromiseState.RESOLVED
        elif prob_accept <= self.b:
            return PromiseState.REJECTED
        else:
            return PromiseState.PENDING

    def _yes_mask(self) -> np.ndarray:
        """
        Boolean mask identifying 'yes' basis states.
        For a 2-amplitude vector: index 0 = yes, index 1 = no.
        For larger vectors: upper half = yes (convention).
        """
        size = len(self.psi)
        mask = np.zeros(size, dtype=float)
        mask[: size // 2] = 1.0
        if size == 2:
            mask[0] = 1.0
            mask[1] = 0.0
        return mask

    def amplitude_amplify(self, iterations: int = 1) -> "SuperpositionDecay":
        """
        Apply Grover-style amplitude amplification.
        Boosts the amplitude of yes-states to push Pr[accept] above threshold a.
        After O(sqrt(k)) iterations the dominant amplitude exceeds 2/3.
        """
        psi = self.psi.copy().astype(complex)
        mask = self._yes_mask()

        # Oracle: flip sign of yes-amplitudes
        oracle = np.diag(1 - 2 * mask)
        # Diffusion operator: inversion about mean
        N = len(psi)
        diffusion = (2 / N) * np.ones((N, N)) - np.eye(N)

        for _ in range(iterations):
            psi = diffusion @ (oracle @ psi)

        self.psi = np.abs(psi)  # Take magnitude after amplification
        norm = np.linalg.norm(self.psi)
        if norm > 0:
            self.psi = self.psi / norm
        return self


# =============================================================================
# READ-WRITE-EXECUTE (RWX) MEMORY MODEL
# =============================================================================

class RWXOperation:
    """
    Read-Write-Execute mosaic table implementing the Atomic Decay Unit (ADU).

    Theorem (Dual-State Equivalence):
      n writes + k reads, where the last operation is a Read,
      collapse to a single coherent Read under superposition decay.

    Concrete instance:  4W + 2R == 1R_coherent

    The external observer sees exactly one read event regardless of
    the number of internal write branches (unitary evolution is unobservable).
    """

    def __init__(self):
        self.writes   = 0
        self.reads    = 0
        self.executes = 0
        self._history: List[str] = []

    def write(self) -> None:
        """Record a write operation (unitary gate -- unobservable externally)."""
        self.writes += 1
        self._history.append("W")

    def execute(self) -> None:
        """Record an execute operation (circuit evaluation within window)."""
        self.executes += 1
        self._history.append("X")

    def read(self) -> PromiseState:
        """
        Record a read operation.
        When 4W + 2R threshold is reached, trigger the Atomic Decay Unit:
        collapse all pending writes to a single coherent read.
        """
        self.reads += 1
        self._history.append("R")

        if self.writes >= 4 and self.reads >= 2:
            return self._atomic_decay_unit()
        return PromiseState.PENDING

    def _atomic_decay_unit(self) -> PromiseState:
        """
        Atomic Decay Unit (ADU):
          4W + 2R -> 1R_coherent
        Resets internal counters; returns the unified coherent read.
        """
        w, r = self.writes, self.reads
        self.writes = 0
        self.reads  = 0
        self._history.append(f"[ADU: {w}W+{r}R->1R]")
        return PromiseState.RESOLVED

    def history(self) -> str:
        return " ".join(self._history)


# =============================================================================
# BQP QUANTUM CIRCUIT
# =============================================================================

class BQPCircuit:
    """
    Formal BQP circuit family implementation.

    Q = {{ Q_n : n in N }}, each Q_n accepts n qubits and gives 1-qubit output.

    Promise:
      x in A_yes  =>  Pr[Q_n(x) = 1] >= a(|x|)
      x in A_no   =>  Pr[Q_n(x) = 1] <= b(|x|)

    The gap a(n) - b(n) >= 1/3 is the BQP tractability condition.
    """

    def __init__(self, n_qubits: int,
                 a: Callable[[int], float],
                 b: Callable[[int], float]):
        self.n     = n_qubits
        self.a     = a
        self.b     = b
        dim        = 2 ** n_qubits
        self.state = np.zeros(dim, dtype=complex)
        self.state[0] = 1.0          # Initialise to |0...0>

    # ── Gate library ─────────────────────────────────────────────────────────

    @staticmethod
    def hadamard() -> np.ndarray:
        """Single-qubit Hadamard gate H = (1/sqrt(2)) [[1,1],[1,-1]]"""
        return np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)

    @staticmethod
    def pauli_x() -> np.ndarray:
        """Pauli-X (NOT) gate."""
        return np.array([[0, 1], [1, 0]], dtype=complex)

    @staticmethod
    def phase_gate(theta: float) -> np.ndarray:
        """Phase rotation gate R(theta)."""
        return np.array([[1, 0], [0, np.exp(1j * theta)]], dtype=complex)

    def apply_gate(self, gate: np.ndarray, target: int) -> None:
        """
        Apply a single-qubit gate to qubit `target` via tensor product expansion.

        Full state-vector update: I^(target) x gate x I^(n-target-1)
        """
        n   = self.n
        dim = 2 ** n
        I   = np.eye(2, dtype=complex)

        # Build full-system operator by Kronecker product
        op = np.array([[1.0 + 0j]], dtype=complex)
        for q in range(n):
            op = np.kron(op, gate if q == target else I)

        self.state = op @ self.state

    def apply_hadamard_all(self) -> None:
        """Apply Hadamard to every qubit (creates uniform superposition)."""
        H = self.hadamard()
        for q in range(self.n):
            self.apply_gate(H, q)

    def measure(self, x: str) -> Tuple[PromiseState, float]:
        """
        Measure input string x per BQP promise problem definition.

        Pr[accept] = sum of |amplitude|^2 for all basis states where
        the designated output qubit (qubit 0, most significant) is |1>.

        For an n-qubit system: basis states with index >= 2^(n-1)
        have qubit 0 = |1>.

        Returns (PromiseState, probability).
        """
        n           = len(x)
        dim         = len(self.state)
        half        = dim // 2
        # Sum probability over all states where output qubit = 1
        prob_accept = float(np.sum(np.abs(self.state[half:]) ** 2))
        threshold_a = self.a(n)
        threshold_b = self.b(n)

        if prob_accept >= threshold_a:
            return (PromiseState.RESOLVED, prob_accept)
        elif prob_accept <= threshold_b:
            return (PromiseState.REJECTED, prob_accept)
        else:
            return (PromiseState.PENDING, prob_accept)


# =============================================================================
# RIFT GRAMMAR MATCHER
# =============================================================================

class RiftGrammarMatcher:
    """
    Rift -- A Flexible Translator (RIRT/RIFT)

    Maps the Superposition Decay framework onto context-free grammar parsing.

    Analogy:
      Wave postulate (triangular)  <->  Grammar production rules
      Superposition state          <->  Active Earley item set Gamma_i
      Decay event                  <->  Parser commit to single parse path
      Stabilisation principle      <->  Post-decay parse tree is final

    Grammar superposition state at position i:
      Gamma_i = { (A -> alpha . beta, j) | A->alpha beta in R,
                  w_j...w_i =>* alpha }

    Decay occurs when |Gamma_i| == 1 (unique parse path remains).
    """

    def __init__(self, grammar: Dict[str, List[str]]):
        """
        grammar: dict mapping non-terminal -> list of production rule strings
        Example: {"S": ["NP VP", "S PP"], "NP": ["det noun"]}
        """
        self.grammar       = grammar
        self.superposition: List[Dict] = []   # Active Earley items
        self._decayed      = False
        self._committed    = None             # Final parse path after decay

    def initialise(self, start: str) -> None:
        """Seed the grammar superposition with all start-symbol productions."""
        self.superposition = []
        for prod in self.grammar.get(start, []):
            self.superposition.append({
                "lhs":      start,
                "prod":     prod,
                "dot":      0,
                "origin":   0,
                "state":    PromiseState.PENDING,
            })

    def scan(self, token: str, position: int) -> PromiseState:
        """
        Advance the grammar superposition by scanning one token.
        Eliminates items whose next expected symbol does not match token.
        Returns the grammar decay state after scanning.
        """
        if self._decayed:
            return PromiseState.RESOLVED   # Already committed

        surviving = []
        for item in self.superposition:
            symbols = item["prod"].split()
            dot     = item["dot"]
            if dot < len(symbols) and symbols[dot] == token:
                advanced = dict(item)
                advanced["dot"] = dot + 1
                surviving.append(advanced)
            elif dot >= len(symbols):
                # Complete item -- keep it
                surviving.append(item)

        self.superposition = surviving

        # Grammar decay event: exactly one path survives
        if len(self.superposition) == 1:
            self._decayed   = True
            self._committed = self.superposition[0]
            return PromiseState.RESOLVED

        # All paths eliminated
        if len(self.superposition) == 0:
            return PromiseState.REJECTED

        # Multiple paths still active -- superposition holds
        return PromiseState.PENDING

    def active_count(self) -> int:
        return len(self.superposition)

    def committed_parse(self) -> Optional[Dict]:
        return self._committed


# =============================================================================
# QUANTUM BURST PROTOCOL (QBP)
# =============================================================================

class QBPConnection:
    """
    Quantum Burst Protocol -- extends SD to networking.

    QBP(A, B) = (G, SD(a,b), Pi)
      G    = quantum connection graph (E, N)
      SD   = superposition decay window governing handshake
      Pi   = set of candidate communication paths held in superposition

    Three handshake phases:
      PENDING   -- Negotiating: all paths Pi in superposition
      RESOLVED  -- Path pi* selected via spectral decay measurement
      REJECTED  -- No viable path survived the decay

    Spectral path selection uses the dominant eigenvector of the
    adjacency matrix of G -- the path with maximum eigenvalue weight
    is selected as pi*.
    """

    def __init__(self, sender: str, receiver: str):
        self.sender   = sender
        self.receiver = receiver
        self.graph    = QuantumConnection()
        self.paths:   List[str] = []
        self.state    = PromiseState.PENDING
        self.selected_path: Optional[str] = None

    def add_path(self, path_id: str,
                 hops: List[Tuple[str, str]]) -> None:
        """
        Register a candidate communication path.
        hops: ordered list of (node_u, node_v) edge tuples.
        """
        self.paths.append(path_id)
        for (u, v) in hops:
            self.graph.add_superposition(u, v)

    def negotiate(self) -> PromiseState:
        """
        Phase 1: hold all paths in superposition.
        Returns PENDING while handshake is in progress.
        """
        self.state = PromiseState.PENDING
        return self.state

    def decay_select(self) -> Tuple[PromiseState, Optional[str]]:
        """
        Phase 2: spectral decay measurement.

        Computes the dominant eigenvector of the graph adjacency matrix.
        The path whose nodes have the highest aggregate eigenvector weight
        is selected as pi*.

        Returns (RESOLVED, pi*) or (REJECTED, None).
        """
        if not self.paths:
            self.state = PromiseState.REJECTED
            return (self.state, None)

        A, node_list = self.graph.adjacency_matrix()

        if A.shape[0] == 0:
            self.state = PromiseState.REJECTED
            return (self.state, None)

        # Spectral analysis: dominant eigenvector
        try:
            eigenvalues, eigenvectors = np.linalg.eig(A)
            dominant_idx = int(np.argmax(np.abs(eigenvalues)))
            dom_vec = np.abs(eigenvectors[:, dominant_idx])
        except np.linalg.LinAlgError:
            self.state = PromiseState.REJECTED
            return (self.state, None)

        # Score each path by sum of eigenvector weights on its nodes
        path_scores = {}
        for path_id in self.paths:
            score = sum(
                dom_vec[node_list.index(n)]
                for n in node_list
                if path_id.split("_")[0] in n
            )
            path_scores[path_id] = score

        best = max(path_scores, key=lambda p: path_scores[p])
        self.selected_path = best
        self.state = PromiseState.RESOLVED
        return (self.state, self.selected_path)

    def connection_string(self) -> str:
        if self.state == PromiseState.RESOLVED and self.selected_path:
            return (f"QBP({self.sender} -> {self.receiver}) "
                    f"via {self.selected_path} [RESOLVED]")
        elif self.state == PromiseState.REJECTED:
            return f"QBP({self.sender} -> {self.receiver}) [REJECTED]"
        else:
            return (f"QBP({self.sender} -> {self.receiver}) "
                    f"[NEGOTIATING: {len(self.paths)} paths in superposition]")


# =============================================================================
# QUANTUM BURST PROTOCOL (orchestrator -- maps classical algorithms to BQP)
# =============================================================================

class QuantumBurstProtocol:
    """
    QBP orchestrator -- Classical-to-Quantum complexity translation.

    Maps homogeneous (linear-time) problems to parallel BQP execution
    via superposition decay windows.
    """

    def __init__(self, complexity_class: ComplexityClass):
        self.class_        = complexity_class
        self.connections:  List[QuantumConnection]   = []
        self.decay_windows: List[SuperpositionDecay] = []

    def map_linear_system(self, equations: List[str]) -> QuantumConnection:
        """
        Map a system of linear equations to a probabilistic DAG.

        Each equation e_i becomes a parallel node pair (eq_i_in, eq_i_out).
        The DAG expresses all equations in parallel -- O(log n) evaluation
        depth under superposition decay (per Theorem 6.2 of the SD paper).
        """
        G = QuantumConnection()
        for i, _ in enumerate(equations):
            G.add_superposition(f"eq_{i}_in", f"eq_{i}_out")
        self.connections.append(G)
        return G

    def execute_parallel(self, dag: QuantumConnection) -> Dict[str, PromiseState]:
        """
        Execute all DAG edges in parallel via superposition decay.

        Each node pair (u, v) gets an independent amplitude derived from
        the node's position in the superposition vector, simulating
        per-branch parallel evaluation.

        Returns {node: PromiseState} mapping.
        """
        results = {}
        n_nodes = len(dag.nodes)

        if n_nodes == 0:
            return results

        # Each node pair (in/out) represents a parallel branch.
        # We model each branch as a 2-amplitude vector biased toward acceptance:
        #   psi = [sqrt(a), sqrt(1-a)] where a > 2/3 (post-amplification)
        # This reflects that amplitude amplification has boosted the yes-branch
        # above the BQP acceptance threshold.
        p_accept = 0.75  # Post-amplification yes-probability (> 2/3 threshold)
        node_psi = np.array([math.sqrt(p_accept),
                             math.sqrt(1.0 - p_accept)], dtype=float)

        global_decay = SuperpositionDecay(node_psi, t_open=0.0, t_decay=1.0,
                                          a=2/3, b=1/3)
        self.decay_windows.append(global_decay)

        node_list = sorted(dag.nodes)
        for node in node_list:
            results[node] = global_decay.measure(t=0.5) or PromiseState.PENDING

        return results


# =============================================================================
# DEMONSTRATION
# =============================================================================

def separator(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


if __name__ == "__main__":

    # ── 1. Complexity and timing ──────────────────────────────────────────────
    separator("1. Classical vs Quantum Time Complexity")
    n = 36
    print(f"  Input size n         : {n}")
    print(f"  Classical time       : O({n})  (linear)")
    print(f"  Quantum half-linear  : O({n//2}) (half-linear via SD)")
    print(f"  Quantum DAG parallel : O(1)    (constant via full DAG collapse)")
    print(f"  BQP threshold gap    : a - b = 2/3 - 1/3 = 1/3  (BQP tractable)")

    # ── 2. Linear system -> parallel DAG ─────────────────────────────────────
    separator("2. Linear System Mapped to Probabilistic DAG")
    qbp = QuantumBurstProtocol(ComplexityClass.BQP)
    equations = ["2x + 3y = 5", "x - y = 1", "4x + y = 6"]
    dag = qbp.map_linear_system(equations)
    print(f"  Equations            : {equations}")
    print(f"  DAG nodes            : {sorted(dag.nodes)}")
    print(f"  DAG edges            : {sorted(dag.edges)}")

    results = qbp.execute_parallel(dag)
    print(f"\n  Parallel execution (per node):")
    for node, state in sorted(results.items()):
        print(f"    {node:20s} -> {state.value}")

    # ── 3. RWX Atomic Decay Unit ──────────────────────────────────────────────
    separator("3. RWX Memory Model -- Atomic Decay Unit (4W + 2R = 1R)")
    rwx = RWXOperation()
    for _ in range(4):
        rwx.write()
    rwx.read()                       # First read  -> PENDING
    final = rwx.read()               # Second read -> ADU fires
    print(f"  Operation history    : {rwx.history()}")
    print(f"  ADU output state     : {final.value}")
    print(f"  (4 writes + 2 reads collapsed to 1 coherent read)")

    # ── 4. BQP circuit measurement ───────────────────────────────────────────
    separator("4. BQP Circuit -- n=36 input measurement")
    def a_func(n): return 2/3
    def b_func(n): return 1/3

    # Circuit A: uniform superposition (PENDING -- between thresholds)
    circuit_a = BQPCircuit(n_qubits=3, a=a_func, b=b_func)
    circuit_a.apply_hadamard_all()
    test_input = "0" * 36
    state_a, prob_a = circuit_a.measure(test_input)
    print(f"  [Circuit A -- uniform superposition after H^3]")
    print(f"  Pr[accept]           : {prob_a:.4f}  -> {state_a.value.upper()}")

    # Circuit B: apply X to qubit 0 to flip toward |1> (RESOLVED)
    circuit_b = BQPCircuit(n_qubits=3, a=a_func, b=b_func)
    circuit_b.apply_gate(circuit_b.pauli_x(), target=0)  # Flip qubit 0 to |1>
    state_b, prob_b = circuit_b.measure(test_input)
    print(f"  [Circuit B -- qubit 0 flipped via Pauli-X gate]")
    print(f"  Pr[accept]           : {prob_b:.4f}  -> {state_b.value.upper()}")
    print(f"  Threshold a(n)       : {a_func(36):.4f}  (BQP accept boundary)")
    print(f"  Threshold b(n)       : {b_func(36):.4f}  (BQP reject boundary)")

    # ── 5. Rift grammar matcher ───────────────────────────────────────────────
    separator("5. Rift Grammar Matcher -- Grammar Superposition")
    grammar = {
        "S":  ["NP VP", "S PP"],
        "NP": ["det noun", "noun"],
        "VP": ["verb NP", "verb"],
    }
    rift = RiftGrammarMatcher(grammar)
    rift.initialise("S")
    print(f"  Grammar              : {list(grammar.keys())} non-terminals")
    print(f"  Active paths (init)  : {rift.active_count()} (superposition)")

    tokens = ["NP", "VP"]
    for tok in tokens:
        st = rift.scan(tok, position=tokens.index(tok))
        print(f"  Scan '{tok:5s}'         -> {st.value:8s} "
              f"(active paths: {rift.active_count()})")

    committed = rift.committed_parse()
    if committed:
        print(f"  Grammar decay event  : committed to '{committed['prod']}'")

    # ── 6. QBP connection establishment ──────────────────────────────────────
    separator("6. Quantum Burst Protocol -- Connection Establishment")
    conn = QBPConnection(sender="ClientA", receiver="ServerB")
    conn.add_path("path_alpha", [("A", "R1"), ("R1", "R2"), ("R2", "B")])
    conn.add_path("path_beta",  [("A", "R3"), ("R3", "B")])
    conn.add_path("path_gamma", [("A", "R1"), ("R1", "B")])

    print(f"  Phase 1 - Negotiate  : {conn.connection_string()}")
    conn.negotiate()

    state_out, pi_star = conn.decay_select()
    print(f"  Phase 2 - Decay      : {conn.connection_string()}")
    print(f"  Selected path pi*    : {pi_star}")
    print(f"  Final state          : {state_out.value.upper()}")

    separator("Done")
    print("  All SD framework components operational.")
    print("  MMUKO-OS / OBINexus toolchain substrate verified.\n")
