<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();

	import { Container } from '@sveltestrap/sveltestrap';
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="d-flex flex-column min-vh-100">
	<Container class="flex-grow-1 d-flex flex-column px-4">
		{@render children()}
	</Container>
</div>
