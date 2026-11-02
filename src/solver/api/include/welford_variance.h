#ifndef WELFORD_VARIANCE_HPP_
#define WELFORD_VARIANCE_HPP_

#include <Kokkos_Core.hpp>

class Welford {
public:
    KOKKOS_INLINE_FUNCTION Welford() = default;
 
    KOKKOS_INLINE_FUNCTION void push(double x) {
        ++n_;
        const double delta = x - mean_;
        mean_ += delta / static_cast<double>(n_);
        m2_ += delta * (x - mean_);
    }
 
    KOKKOS_INLINE_FUNCTION void merge(const Welford& o) {
        if (o.n_ == 0) return;
        if (n_ == 0) { *this = o; return; }
        const double na = static_cast<double>(n_);
        const double nb = static_cast<double>(o.n_);
        const double n  = na + nb;
        const double delta = o.mean_ - mean_;
        mean_ += delta * nb / n;
        m2_   += o.m2_ + delta * delta * na * nb / n;
        n_    += o.n_;
    }
 
    KOKKOS_INLINE_FUNCTION std::size_t count() const { return n_; }
 
    KOKKOS_INLINE_FUNCTION double mean() const {
        return n_ ? mean_ : nan();
    }
    KOKKOS_INLINE_FUNCTION double variance_population() const {
        return n_ ? m2_ / static_cast<double>(n_) : nan();
    }
    KOKKOS_INLINE_FUNCTION double variance() const {
        return n_ > 1 ? m2_ / static_cast<double>(n_ - 1) : nan();
    }
    KOKKOS_INLINE_FUNCTION double stddev() const {
        return Kokkos::sqrt(variance());
    }
    KOKKOS_INLINE_FUNCTION double stddev_population() const {
        return Kokkos::sqrt(variance_population());
    }
 
private:
    KOKKOS_INLINE_FUNCTION static double nan() {
        return Kokkos::Experimental::quiet_NaN_v<double>;
    }
 
    std::size_t n_ = 0;
    double mean_ = 0.0;
    double m2_ = 0.0;
};
 
// Custom Kokkos reducer so Welford can be used directly with
// Kokkos::parallel_reduce, including with lambdas.
template <class Space = Kokkos::HostSpace>
struct WelfordReducer {
    using reducer          = WelfordReducer;
    using value_type       = Welford;
    using result_view_type = Kokkos::View<value_type, Space,
                                          Kokkos::MemoryUnmanaged>;
 
    value_type* value;
 
    KOKKOS_INLINE_FUNCTION explicit WelfordReducer(value_type& v) : value(&v) {}
 
    KOKKOS_INLINE_FUNCTION void join(value_type& dest,
                                     const value_type& src) const {
        dest.merge(src);
    }
    KOKKOS_INLINE_FUNCTION void init(value_type& v) const { v = value_type(); }
    KOKKOS_INLINE_FUNCTION value_type& reference() const { return *value; }
    KOKKOS_INLINE_FUNCTION result_view_type view() const {
        return result_view_type(value);
    }
    KOKKOS_INLINE_FUNCTION bool references_scalar() const { return true; }
};


#endif /* WELFORD_VARIANCE_HPP_ */